#!/bin/bash

# API Testing Dashboard Launcher
# This script opens the API testing dashboard in your default browser

echo "🧪 API Testing Dashboard Launcher"
echo "=================================="

# Check if server is running
if curl -s "http://127.0.0.1:5000/" > /dev/null 2>&1; then
    echo "✅ Server is running on http://127.0.0.1:5000"
    echo "🚀 Opening API Testing Dashboard..."
    
    # Open in default browser
    if command -v open > /dev/null 2>&1; then
        # macOS
        open "http://127.0.0.1:5000/api_testing"
    elif command -v xdg-open > /dev/null 2>&1; then
        # Linux
        xdg-open "http://127.0.0.1:5000/api_testing"
    elif command -v start > /dev/null 2>&1; then
        # Windows
        start "http://127.0.0.1:5000/api_testing"
    else
        echo "📋 Manual access: http://127.0.0.1:5000/api_testing"
    fi
    
    echo ""
    echo "📖 Available test users:"
    echo "   • acmeadmin / password123 (Admin - Full access)"
    echo "   • test / test123 (Regular User - Limited access)"
    echo "   • globexmgr / password123 (Regular User - Limited access)"
    echo ""
    echo "📚 See API_TESTING_GUIDE.md for detailed instructions"
    
else
    echo "❌ Server is not running on http://127.0.0.1:5000"
    echo ""
    echo "🔧 To start the server:"
    echo "   cd back_end"
    echo "   python app.py"
    echo ""
    echo "Then run this script again."
fi
