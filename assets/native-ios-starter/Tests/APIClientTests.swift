import XCTest
@testable import __SWIFT_NAME__

final class APIClientTests: XCTestCase {
    func testEndpointAppendsPathComponentsSafely() {
        let endpoint = APIEndpoint(path: "/v1/items")

        let url = endpoint.url(relativeTo: URL(string: "https://api.example.com")!)

        XCTAssertEqual(url.absoluteString, "https://api.example.com/v1/items")
    }
}
