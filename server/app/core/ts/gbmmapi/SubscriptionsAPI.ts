import axios from "axios";
import {ResponseData} from "./API";

export enum MessageSubjectType {
    Download
}

export enum MessageEventType {
    Created = 0,
    Modified = 1,
    Deleted = 2
}

export interface Message {
    event_type: MessageEventType;
    subject_type: MessageSubjectType;
    subject_id: any;
    data: any;
}


export function AllMessageEventTypes() {
    return new Set([
        MessageEventType.Created,
        MessageEventType.Modified,
        MessageEventType.Deleted
    ]);
}

export interface GetSubscriptionData extends ResponseData {
    subscription_valid: boolean;
    messages: Message[];
}

export interface NewSubscriptionData extends ResponseData {
    uuid: string;
}

export interface InterestsParams {
    interests: InterestsParam[];
}


export interface InterestsParam {
    subjectType: MessageSubjectType;
    eventType: Set<MessageEventType>;
}

export default class SubscriptionsAPI {
    public static subscribe() {
        return axios.post<NewSubscriptionData>(`/api/subscriptions/subscribe`, {});
    }

    public static unsubscribe(uuid: string) {
        return axios.post(`/api/subscriptions/${uuid}/unsubscribe`);
    }

    public static get(uuid: string) {
        return axios.post<GetSubscriptionData>(`/api/subscriptions/${uuid}/get`);
    }

    public static addInterests(uuid: string, data: InterestsParams) {
        return axios.post(`/api/subscriptions/${uuid}/add-interests`, data);
    }

    public static removeInterests(uuid: string, data: InterestsParams) {
        return axios.post(`/api/subscriptions/${uuid}/remove-interests`, data);
    }

    public static setInterests(uuid: string, data: InterestsParams) {
        return axios.post(`/api/subscriptions/${uuid}/set-interests`, data);
    }
}