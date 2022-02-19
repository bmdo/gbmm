// https://stackoverflow.com/a/14657922

export interface ILiteEvent<T> {
    on(handler: { (data?: T): any }): void;
    off(handler: { (data?: T): any }): void;
}

export default class LiteEvent<T> {
    private handlers: { (data?: T): void; }[] = [];

    public on(handler: { (data?: T): any }) {
        this.handlers.push(handler);
    }

    public off(handler: { (data?: T): any }) {
        this.handlers = this.handlers.filter(h => h !== handler);
    }

    public trigger(data?: T) {
        for (const handler of this.handlers.slice(0)) {
            handler(data);
        }
    }

    public expose() {
        return this;
    }
}