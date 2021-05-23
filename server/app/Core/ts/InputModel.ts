import ValidationResult from "./ValidationResult";

export default class InputModel<T> {
    private _value: T
    public validator: (v: T) => ValidationResult
    public validateOn: 'input' = 'input'

    public initialized = false
    public modified = false

    private validationOverride: ValidationResult = null
    private onValidCallbacks: Array<(v?: T) => any> = []
    private onInvalidCallbacks: Array<(v?: T) => any> = []

    public constructor(value: T = null, validator: (v: T) => ValidationResult = null) {
        this._value = value;
        this.validator = validator;
        this.initialized = true;
    }

    private get validateOnInput(): boolean { return this.validateOn === 'input' }

    public get value(): T {
        return this._value;
    }

    public set value(v: T) {
        if (this.initialized && this._value !== v) {
            this.modified = true;
        }
        this._value = v;
        if (this.validateOnInput) {
            this.validate();
        }
    }

    private validate(): ValidationResult {
        return this.validator?.(this.value) ?? new ValidationResult(true);
    }

    public invalidate(msg: string) {
        this.validationOverride = new ValidationResult(false, msg);
    }

    public get valid(): boolean {
        let valid = this.validationOverride?.valid ?? this.validate().valid;
        if (valid) {
            this.onValidCallbacks.forEach((cb) => { cb(this.value) });
        }
        else {
            this.onInvalidCallbacks.forEach((cb) => { cb(this.value) });
        }
        return valid;
    }

    public get validationFeedback(): string {
        return this.validationOverride?.message ?? this.validate().message;
    }

    public onValid(callback: (v?: T) => any) {
        this.onValidCallbacks.push(callback)
    }

    public onInvalid(callback: (v?: T) => any) {
        this.onInvalidCallbacks.push(callback)
    }

    public resetModified() {
        this.modified = false
    }
}