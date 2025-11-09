#!/bin/bash
# Open Developer Documentation
# This script opens the HospiTwin Lite developer documentation in your default browser

echo "🏥 HospiTwin Lite - Developer Documentation"
echo "==========================================="
echo ""

# Check if docs/index.html exists
if [ ! -f "docs/index.html" ]; then
    echo "❌ Error: docs/index.html not found!"
    echo "   Please ensure you're running this script from the project root directory."
    exit 1
fi

# Get the absolute path
DOCS_PATH="$(pwd)/docs/index.html"

echo "📖 Opening documentation: $DOCS_PATH"
echo ""

# Detect OS and open appropriately
case "$(uname -s)" in
    Darwin*)
        # macOS
        open "$DOCS_PATH"
        echo "✅ Documentation opened in default browser (macOS)"
        ;;
    Linux*)
        # Linux
        if command -v xdg-open > /dev/null; then
            xdg-open "$DOCS_PATH"
            echo "✅ Documentation opened in default browser (Linux)"
        else
            echo "⚠️  Could not detect browser launcher."
            echo "   Please open this file manually: $DOCS_PATH"
        fi
        ;;
    MINGW*|MSYS*|CYGWIN*)
        # Windows (Git Bash, MSYS, Cygwin)
        start "$DOCS_PATH"
        echo "✅ Documentation opened in default browser (Windows)"
        ;;
    *)
        echo "⚠️  Unknown operating system."
        echo "   Please open this file manually: $DOCS_PATH"
        ;;
esac

echo ""
echo "📡 To use the Interactive Test Runner:"
echo "   1. Ensure backend server is running: uvicorn app.main:app --reload"
echo "   2. Navigate to the '🧪 Integration Tests' tab"
echo "   3. Click 'Run All Tests' button"
echo ""
echo "📚 For more information, see: docs/README.md"
