import Foundation

enum APIError: Error, Equatable {
    case invalidResponse
    case unexpectedStatus(Int)
}

struct APIEndpoint: Equatable, Sendable {
    let path: String

    func url(relativeTo baseURL: URL) -> URL {
        path.split(separator: "/").reduce(baseURL) { url, component in
            url.appending(path: String(component))
        }
    }
}

actor APIClient {
    private let baseURL: URL
    private let session: URLSession
    private let decoder: JSONDecoder

    init(baseURL: URL, session: URLSession = .shared, decoder: JSONDecoder = JSONDecoder()) {
        self.baseURL = baseURL
        self.session = session
        self.decoder = decoder
    }

    func get<Response: Decodable & Sendable>(
        _ endpoint: APIEndpoint,
        as type: Response.Type = Response.self
    ) async throws -> Response {
        var request = URLRequest(url: endpoint.url(relativeTo: baseURL))
        request.httpMethod = "GET"
        request.timeoutInterval = 30

        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        guard 200..<300 ~= http.statusCode else {
            throw APIError.unexpectedStatus(http.statusCode)
        }
        return try decoder.decode(Response.self, from: data)
    }
}
