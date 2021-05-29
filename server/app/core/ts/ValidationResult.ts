export default class ValidationResult {
    public valid: boolean
    public message: string

    constructor(valid: boolean, message: string = null) {
        this.valid = valid;
        this.message = message;
    }

    public static FromServerResponse(responseData: any): ValidationResult {
        return new ValidationResult(responseData.valid, responseData.message)
    }
}