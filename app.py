"""
app.py
Flask application template for the warm-up assignment

Students need to implement the API endpoints as specified in the assignment.
"""

from flask import Flask, request, jsonify, render_template
from starter_preprocess import TextPreprocessor
import traceback

app = Flask(__name__)
preprocessor = TextPreprocessor()

@app.route('/')
def home():
    """Render a simple HTML form for URL input"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Text preprocessing service is running"
    })

@app.route('/api/clean', methods=['POST'])
def clean_text():
    try:
        data = request.get_json(force=True, silent=True) or {}
        url = (data.get("url") or "").strip()
        if not url:
            return jsonify({"success": False, "error": "Missing 'url' in JSON body."}), 400

        raw = preprocessor.fetch_from_url(url)
        cleaned_core = preprocessor.clean_gutenberg_text(raw)

        stats = preprocessor.get_text_statistics(cleaned_core)
        summary = preprocessor.create_summary(cleaned_core, num_sentences=3)

        return jsonify({
            "success": True,
            "cleaned_text": cleaned_core[:2000],  # short preview
            "statistics": stats,
            "summary": summary,
            "error": None
        }), 200

    except Exception as e:
        app.logger.exception(e)
        return jsonify({"success": False, "error": str(e)}), 500
    

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    try:
        data = request.get_json(force=True, silent=True) or {}
        text = data.get("text")
        if not isinstance(text, str) or not text.strip():
            return jsonify({"success": False, "error": "Missing non-empty 'text' in JSON body."}), 400

        stats = preprocessor.get_text_statistics(text)
        summary = preprocessor.create_summary(text, num_sentences=3)

        return jsonify({"success": True, "statistics": stats, "summary": summary, "error": None}), 200

    except Exception as e:
        app.logger.exception(e)
        return jsonify({"success": False, "error": str(e)}), 500
    
# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Text Preprocessing Web Service...")
    print("📖 Available endpoints:")
    print("   GET  /           - Web interface")
    print("   GET  /health     - Health check")
    print("   POST /api/clean  - Clean text from URL")
    print("   POST /api/analyze - Analyze raw text")
    print()
    print("🌐 Open your browser to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    
    app.run(debug=True, port=5000, host='0.0.0.0')