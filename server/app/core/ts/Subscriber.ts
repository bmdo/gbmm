import API from "./gbmmapi/API";
import {AllMessageEventTypes, Message, MessageEventType, MessageSubjectType} from "./gbmmapi/SubscriptionsAPI";
import GbmmVue from "./GbmmVue";
import LiteEvent from "./LiteEvent";
import {parse as uuidParse, stringify as uuidStringify} from "uuid";

class SubscriptionPoller {
    private active: boolean;
    private starting: boolean;
    private stopping: boolean;
    private polling: boolean;
    private interval: number;
    private serverSubscriptionUuid: string;
    private readonly intervalTimeout: number;
    private interestManager: PollerInterestManager;
    private shouldStop: boolean;

    /**
     * Create a SubscriptionPoller.
     * @param intervalTimeout The interval between polling requests in milliseconds.
     */
    public constructor(intervalTimeout: number) {
        this.intervalTimeout = intervalTimeout;
        this.interestManager = new PollerInterestManager();
        this.interestManager.interestsUpdated.on(this.setInterests);
        this.active = false;
        this.starting = false;
        this.stopping = false;
        this.shouldStop = false;
        this.polling = false;
    }

    public start() {
        if (!this.active) {
            this.active = true;
            this.starting = true;
            API.subscriptions.subscribe()
                .then(response => {
                    this.starting = false;
                    this.serverSubscriptionUuid = uuidStringify(uuidParse(response.data.uuid));
                    this.setInterests();
                    this.interval = window.setInterval(this.poll, this.intervalTimeout);
                })
                .catch(reason => {
                    this.active = false;
                    this.starting = false;
                    console.error(`Failed to start subscription poller: ${reason}`)
                })
                .finally(() => {
                    if (this.shouldStop) {
                        this.stop();
                    }
                })
        }
    }

    public stop() {
        this.shouldStop = false;
        if (this.stopping) {
            console.warn('Attempted to stop poller while the poller was already stopping');
            return;
        }
        else if (this.starting) {
            // If the poller is in the process of starting, we'll set shouldStop to true, which the start process will
            // find when it finishes and will immediately stop the poller.
            this.shouldStop = true;
        }
        else if (this.active) {
            this.stopping = true;
            window.clearInterval(this.interval);
            if (this.serverSubscriptionUuid !== undefined) {
                API.subscriptions.unsubscribe(this.serverSubscriptionUuid)
                .then(() => {
                    this.stopping = false;
                    this.active = false;
                })
                .catch(reason => {
                    console.error(`Failed to stop subscription poller: ${reason}`);
                    this.stopping = false;
                });
            }
        }
    }

    public error(msg?: string) {
        if (msg === undefined) {
            msg = 'No error message provided.';
        }
        console.error(`Subscription poller encountered an error: ${msg}`);
        console.error('Attempting to stop subscription poller.');
        try {
            // Try to stop the poller
            this.stop();
        }
        catch {
            console.error('First attempt to stop subscription poller after error failed. Will try once more.')
            // If that fails for some reason, continue to try again after a timeout.
            window.setTimeout(() => this.stop(), 1000);
        }
    }

    public add(subscriber: Subscriber) {
        this.interestManager.addSubscriber(subscriber);
    }

    public remove(subscriber: Subscriber) {
        this.interestManager.removeSubscriber(subscriber);
    }

    public setInterests = () => {
        if (this.active && this.serverSubscriptionUuid !== undefined) {
            API.subscriptions.setInterests(this.serverSubscriptionUuid, {interests: this.interestManager.getUniqueInterests()})
            .catch(reason => {
                console.error(`Failed to set interests: ${reason}`);
            });
        }
    }

    private poll = () => {
        if (this.active && this.serverSubscriptionUuid !== undefined && !this.polling) {
            this.polling = true;
            API.subscriptions.get(this.serverSubscriptionUuid)
                .then(response => {
                    if (!response.data.subscription_valid) {
                        this.error('Subscription invalidated.');
                    }
                    else {
                        for (const message of response.data.messages) {
                            const subscribers = this.interestManager.getSubscribersInterestedInMessage(message);
                            for (const subscriber of subscribers) {
                                subscriber.deliver(message);
                            }
                        }
                    }
                })
                .catch(reason => {
                    console.error(`Failed to poll subscription: ${reason}`);
                })
                .finally(() => {
                    this.polling = false;
                });
        }
    }
}

export interface Subscriber {
    get subscriber_id(): number;
    get interests(): Interest[];
    receive_message(message: Message): any;
    addInterest(interest: Interest): void;
    addInterest(subjectType: MessageSubjectType, eventType?: Set<MessageEventType>): void;
    removeInterest(interest: Interest): void;
    removeInterest(subjectType: MessageSubjectType, eventType?: Set<MessageEventType>): void;
    deliver(message: Message): void;
    interestsUpdated: LiteEvent<Subscriber>;
}

export default abstract class SubscriberVue extends GbmmVue implements Subscriber {
    private static lastId: number = 0;

    private static generateId(): number {
        return SubscriberVue.lastId++;
    }

    private readonly subscriberId_: number;
    public get subscriber_id() {
        return this.subscriberId_;
    }

    private interests_: Interest[];
    public get interests() {
        return this.interests_.slice(0);
    }

    public interestsUpdated: LiteEvent<Subscriber>;

    public abstract receive_message(message: Message): any;

    public constructor() {
        super();
        this.subscriberId_ = SubscriberVue.generateId();
        this.interests_ = [];
        this.interestsUpdated = new LiteEvent<Subscriber>();
        poller.add(this);
    }

    public addInterest(interest: Interest): void;
    public addInterest(subjectType: MessageSubjectType, eventType?: Set<MessageEventType>): void;
    public addInterest(arg1: Interest | MessageSubjectType, eventType?: Set<MessageEventType>) {
        let interest = this.handleInterestArgs(arg1, eventType);
        let found = this.findInterest(interest);
        if (found !== undefined) {
            // If we are already interested in this subjectType, merge the existing eventType list with the incoming
            // eventType list.
            interest.eventType.forEach(eventType => {
                found.eventType.add(eventType);
            });
        }
        else {
            // We were not already interested in this subjectType, so add this as a new entry.
            this.interests_.push(interest);
        }

        this.interestsUpdated.trigger(this);
    }

    public removeInterest(interest: Interest): void;
    public removeInterest(subjectType: MessageSubjectType, eventType?: Set<MessageEventType>): void;
    public removeInterest(arg1: Interest | MessageSubjectType, eventType?: Set<MessageEventType>) {
        let interest = this.handleInterestArgs(arg1, eventType);
        let found = this.findInterest(interest);
        if (found !== undefined) {
            // If we were interested in this subjectType, remove any existing eventTypes that match the incoming
            // eventTypes.
            interest.eventType.forEach(eventType => {
                found.eventType.delete(eventType);
            });
            if (found.eventType.size < 1) {
                // If we removed all eventTypes from the interest, remove the interest entirely.
                this.interests_ = this.interests_.filter(i => i !== found);
            }
        }

        this.interestsUpdated.trigger(this);
    }

    public deliver(message: Message) {
        this.receive_message(message);
    }

    private handleInterestArgs(arg1: Interest | MessageSubjectType, eventType?: Set<MessageEventType>) {
        let interest: Interest;
        if (arg1 instanceof Interest) {
            interest = arg1;
        }
        else {
            if (eventType == undefined) {
                eventType = AllMessageEventTypes();
            }
            interest = new Interest(arg1, eventType);
        }
        return interest;
    }

    private findInterest(interest: Interest) {
        if (interest.eventType.size < 1) {
            // If this interest contains no eventTypes, do not return any interests.
            return;
        }
        return this.interests_.find(v => v.subjectType == interest.subjectType);
    }


}

export class Interest {
    subjectType: MessageSubjectType;
    eventType: Set<MessageEventType>;

    public constructor(subjectType: MessageSubjectType, eventType?: Set<MessageEventType>) {
        this.subjectType = subjectType;
        if (eventType === undefined) {
            // If no eventType is supplied, assume all eventTypes.
            this.eventType = new Set<MessageEventType>();
            for (const e of Object.values(MessageEventType)) {
                this.eventType.add(<MessageEventType>e);
            }
        }
        else {
            this.eventType = eventType;
        }
    }

    public addEventType(eventType: MessageEventType) {
        this.eventType.add(eventType);
    }
}

class PollerInterestManager {
    private readonly interestsToSubscribers: {[subjectType: string]: {[eventType: number]: Subscriber[]}};
    private uniqueInterests: Interest[];
    private uniqueInterestRecalculationNeeded: boolean;

    public interestsUpdated: LiteEvent<PollerInterestManager>;

    public constructor() {
        this.interestsToSubscribers = {};
        this.uniqueInterests = [];
        this.uniqueInterestRecalculationNeeded = false;
        this.interestsUpdated = new LiteEvent<PollerInterestManager>();
    }

    public addSubscriber(subscriber: Subscriber) {
        this.addAllSubscriberInterests(subscriber);
        subscriber.interestsUpdated.on(this.subscriberInterestsUpdatedHandler);
        this.markInterestsUpdated();
    }

    public removeSubscriber(subscriber: Subscriber) {
        this.removeAllSubscriberInterests(subscriber);
        subscriber.interestsUpdated.off(this.subscriberInterestsUpdatedHandler);
        this.markInterestsUpdated();
    }

    public getSubscribersForInterest(subjectType: MessageSubjectType, eventType: MessageEventType): Subscriber[] | undefined {
        let eventTypes = this.interestsToSubscribers[subjectType];
        if (eventTypes === undefined) {
            return [];
        }
        if (eventTypes[eventType] === undefined) {
            return [];
        }
        return eventTypes[eventType].slice(); // Return a copy
    }

    public getSubscribersInterestedInMessage(message: Message): Subscriber[] {
        return this.getSubscribersForInterest(message.subject_type, message.event_type);
    }

    public getUniqueInterests() {
        if (this.uniqueInterestRecalculationNeeded) {
            this.uniqueInterests = [];
            for (const subjectTypeKey in this.interestsToSubscribers) {
                const subjectType: MessageSubjectType = <MessageSubjectType>subjectTypeKey;
                let interest = new Interest(subjectType, new Set<MessageEventType>());
                for (const eventTypeKey in this.interestsToSubscribers[subjectType]) {
                    const eventType: MessageEventType = parseInt(eventTypeKey);
                    interest.addEventType(eventType);
                }
                this.uniqueInterests.push(interest);
            }
            this.uniqueInterestRecalculationNeeded = false;
        }
        return this.uniqueInterests;
    }

    private addSubscriberInterest(subjectType: MessageSubjectType, eventType: MessageEventType, subscriber: Subscriber) {
        let eventTypes = this.interestsToSubscribers[subjectType];
        if (eventTypes === undefined) {
            eventTypes = [];
            this.interestsToSubscribers[subjectType] = eventTypes;
        }
        let subscribers = this.interestsToSubscribers[subjectType][eventType];
        if (subscribers === undefined) {
            subscribers = []
            this.interestsToSubscribers[subjectType][eventType] = subscribers;
        }
        if (subscribers.indexOf(subscriber) < 0) { // Avoid duplicates
            subscribers.push(subscriber);
        }
    }

    private addAllSubscriberInterests(subscriber: Subscriber) {
        for (const interest of subscriber.interests) {
            interest.eventType.forEach(individualEventType => {
                this.addSubscriberInterest(interest.subjectType, individualEventType, subscriber);
            });
        }
    }

    private removeSubscriberInterest(subjectType: MessageSubjectType, eventType: MessageEventType, subscriber: Subscriber) {
        let eventTypes = this.interestsToSubscribers[subjectType];
        if (eventTypes === undefined) {
            return;
        }
        let subscribers = eventTypes[eventType];
        if (subscribers === undefined) {
            return;
        }
        subscribers.filter(v => v === subscriber);
    }

    private removeAllSubscriberInterests(subscriber: Subscriber) {
        //  ENHANCE This would be more efficient if we store an index of subscribers to interests as well, and maintain
        //      both simultaneously. Currently just looping through every list that exists. This optimization probably
        //      isn't useful unless total subscribers grows large.
        for (const subjectTypeKey in this.interestsToSubscribers) {
            const subjectType: MessageSubjectType = <MessageSubjectType>subjectTypeKey;
            for (const eventTypeKey in this.interestsToSubscribers[subjectTypeKey]) {
                const eventType = parseInt(eventTypeKey);
                this.removeSubscriberInterest(subjectType, eventType, subscriber);
            }
        }
    }

    private subscriberInterestsUpdatedHandler = (subscriber: Subscriber) => {
        this.removeAllSubscriberInterests(subscriber);
        this.addAllSubscriberInterests(subscriber);
        this.markInterestsUpdated();
    }

    private markInterestsUpdated() {
        this.uniqueInterestRecalculationNeeded = true;
        this.interestsUpdated.trigger(this);
    }
}

let poller = new SubscriptionPoller(1000);
poller.start();
