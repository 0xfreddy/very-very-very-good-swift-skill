import SwiftUI

enum AppTheme {
    enum Spacing {
        static let compact: CGFloat = 8
        static let standard: CGFloat = 16
        static let section: CGFloat = 24
    }

    enum Shape {
        static let controlRadius: CGFloat = 12
    }

    static let canvas = Color(uiColor: .systemBackground)
    static let surface = Color(uiColor: .secondarySystemBackground)
    static let primaryText = Color.primary
    static let secondaryText = Color.secondary
    static let accent = Color.accentColor
}
