import SwiftUI

struct AppRootView: View {
    var body: some View {
        NavigationStack {
            ContentUnavailableView {
                Label("__APP_NAME__", systemImage: "sparkles")
            } description: {
                Text("Replace this state with the first complete user loop.")
            } actions: {
                NavigationLink("Open starter screen") {
                    StarterScreen()
                }
                .buttonStyle(.borderedProminent)
            }
            .navigationTitle("__APP_NAME__")
        }
    }
}

private struct StarterScreen: View {
    var body: some View {
        List {
            Section("Build vertically") {
                Label("Connect one real data source", systemImage: "network")
                Label("Model empty, error, and offline states", systemImage: "exclamationmark.triangle")
                Label("Add tests and accessibility", systemImage: "checkmark.seal")
            }
        }
        .navigationTitle("Starter")
    }
}
