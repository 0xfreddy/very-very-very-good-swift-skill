import Foundation
import Testing
@testable import __SWIFT_NAME__

@Test("Endpoint appends path components safely", arguments: [
    ("/v1/items", "https://api.example.com/v1/items"),
    ("v1/search", "https://api.example.com/v1/search"),
])
func endpointAppendsPathComponentsSafely(path: String, expectedURL: String) throws {
    let baseURL = try #require(URL(string: "https://api.example.com"))
    let endpoint = APIEndpoint(path: path)

    #expect(endpoint.url(relativeTo: baseURL).absoluteString == expectedURL)
}
