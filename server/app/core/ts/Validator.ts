import ValidationResult from "./ValidationResult";

export default class ValidatorFactory {
    public static Simple<T>(tester: (v: T) => boolean, invalidFeedback: string = null) {
        return (v: T) => {
            let valid = tester(v)
            let feedback = null
            if (!valid) {
                feedback = invalidFeedback
            }
            return new ValidationResult(valid, feedback)
        }
    }
}