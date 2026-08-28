import Foundation

enum AppConfiguration {
    static var apiBaseURL: URL {
        guard
            let value = Bundle.main.object(forInfoDictionaryKey: "API_BASE_URL") as? String,
            let url = URL(string: value),
            url.scheme == "https"
        else {
            preconditionFailure("API_BASE_URL must be a valid HTTPS URL in the active configuration")
        }
        return url
    }
}
