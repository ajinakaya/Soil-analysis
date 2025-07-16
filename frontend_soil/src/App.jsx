import React, { useState } from 'react';
import { UploadCloud, CheckCircle, XCircle, Loader, Info, Leaf, Microscope, Camera, TrendingUp, Droplets, Sun } from 'lucide-react';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = 'http://localhost:5000/predict';

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setPredictionResult(null);
      setError(null);
    } else {
      setSelectedFile(null);
      setPreviewUrl(null);
      setPredictionResult(null);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile) {
      setError("Please select an image to upload.");
      return;
    }

    setLoading(true);
    setError(null);
    setPredictionResult(null);

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPredictionResult(data);
    } catch (err) {
      console.error("Prediction failed:", err);
      setError(err.message || "Failed to get prediction. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getPhColorClass = (ph) => {
    if (!ph) return 'text-gray-600';
    const phNum = parseFloat(ph);
    if (phNum < 6.0) return 'text-orange-600';
    if (phNum > 6.8) return 'text-blue-600';
    return 'text-green-600';
  };

  const getPhStatus = (ph) => {
    if (!ph) return 'Unknown';
    const phNum = parseFloat(ph);
    if (phNum < 6.0) return 'Too Acidic';
    if (phNum > 6.8) return 'Too Alkaline';
    return 'Optimal for Tomatoes';
  };

  const renderLoadingState = () => (
    <div className="flex flex-col items-center justify-center py-16 px-8">
      <div className="relative">
        <div className="w-20 h-20 border-4 border-emerald-200 rounded-full animate-spin border-t-emerald-500"></div>
        <Microscope className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 h-8 w-8 text-emerald-600" />
      </div>
      <h3 className="text-2xl font-semibold text-gray-800 mt-6 mb-2">Analyzing Your Soil</h3>
      <p className="text-gray-600 text-center max-w-sm">Our AI is examining your soil sample using advanced machine learning algorithms...</p>
      <div className="flex space-x-1 mt-4">
        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
      </div>
    </div>
  );

  const renderErrorState = () => (
    <div className="flex flex-col items-center justify-center py-16 px-8 text-center">
      <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mb-6">
        <XCircle className="h-10 w-10 text-red-500" />
      </div>
      <h3 className="text-2xl font-semibold text-gray-800 mb-2">Analysis Failed</h3>
      <p className="text-gray-600 max-w-sm">{error}</p>
      <button
        onClick={() => setError(null)}
        className="mt-6 px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
      >
        Try Again
      </button>
    </div>
  );

  const renderResults = () => (
    <div className="space-y-8">
      {/* Main Result Card */}
      <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 rounded-2xl p-8">
        <div className="flex items-center justify-center mb-6">
          <div className="w-16 h-16 bg-emerald-500 rounded-full flex items-center justify-center">
            <Microscope className="h-8 w-8 text-white" />
          </div>
        </div>
        <h3 className="text-3xl font-bold text-center text-gray-800 mb-2">
          {predictionResult.predicted_soil_type}
        </h3>
        <div className="text-center mb-6">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-emerald-100 text-emerald-800">
            {predictionResult.confidence}% Confidence
          </span>
        </div>

        {/* pH Information */}
        {predictionResult.predicted_pH && (
          <div className="bg-white rounded-xl p-6 border border-emerald-100">
            <div className="grid grid-cols-2 gap-6">
              <div className="text-center">
                <Droplets className="h-8 w-8 mx-auto mb-2 text-blue-500" />
                <h4 className="text-lg font-semibold text-gray-700">pH Level</h4>
                <p className={`text-3xl font-bold ${getPhColorClass(predictionResult.predicted_pH)}`}>
                  {predictionResult.predicted_pH}
                </p>
                <p className={`text-sm font-medium ${getPhColorClass(predictionResult.predicted_pH)}`}>
                  {getPhStatus(predictionResult.predicted_pH)}
                </p>
              </div>
              <div className="text-center">
                <TrendingUp className="h-8 w-8 mx-auto mb-2 text-emerald-500" />
                <h4 className="text-lg font-semibold text-gray-700">Soil Quality</h4>
                <p className="text-3xl font-bold text-emerald-600">Good</p>
                <p className="text-sm text-gray-500">For Tomato Growth</p>
              </div>
            </div>
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <p className="text-xs text-blue-700 text-center">
                💡 Optimal pH range for tomatoes: 6.0 - 6.8
              </p>
            </div>
          </div>
        )}

        {/* Confidence Chart */}
        {predictionResult.chart_image && (
          <div className="mt-6">
            <h4 className="text-lg font-semibold text-gray-700 mb-3">Prediction Breakdown</h4>
            <div className="bg-white rounded-xl p-4 border border-emerald-100">
              <img 
                src={`data:image/png;base64,${predictionResult.chart_image}`} 
                alt="Prediction Confidence Chart"
                className="w-full h-auto rounded-lg"
              />
            </div>
          </div>
        )}
      </div>

      {/* Recommendations Card */}
      <div className="bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded-2xl p-8">
        <div className="flex items-center mb-6">
          <div className="w-12 h-12 bg-amber-500 rounded-full flex items-center justify-center mr-4">
            <Leaf className="h-6 w-6 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-800">Expert Recommendations</h3>
        </div>
        <div className="prose prose-gray max-w-none">
          <p className="text-gray-700 leading-relaxed text-lg">
            {predictionResult.recommendations}
          </p>
        </div>
        <div className="mt-8 pt-6 border-t border-amber-200">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span className="flex items-center">
              <Info className="h-4 w-4 mr-2" />
              Analysis completed
            </span>
            <span>{new Date(predictionResult.timestamp).toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderUploadArea = () => (
    <div className="text-center py-16 px-8">
      <div className="max-w-md mx-auto">
        <label htmlFor="image-upload" className="cursor-pointer block">
          <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-emerald-400 to-teal-500 rounded-full flex items-center justify-center hover:from-emerald-500 hover:to-teal-600 transition-all duration-300 transform hover:scale-105">
            <Camera className="h-12 w-12 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-800 mb-2">Upload Soil Image</h3>
          <p className="text-gray-600 mb-6">Click to select an image of your soil sample</p>
          <div className="border-2 border-dashed border-emerald-300 rounded-2xl p-8 hover:border-emerald-400 hover:bg-emerald-50 transition-all duration-300">
            <UploadCloud className="h-16 w-16 text-emerald-500 mx-auto mb-4" />
            <p className="text-lg font-medium text-emerald-700">Choose Image File</p>
            <p className="text-sm text-gray-500 mt-2">JPEG, PNG, or GIF • Optimized for 224×224px</p>
          </div>
        </label>
        <input
          id="image-upload"
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />
      </div>
    </div>
  );

  const renderImagePreview = () => (
    <div className="space-y-6">
      {/* Image Preview */}
      <div className="bg-white rounded-2xl p-6 border border-gray-200 shadow-sm">
        <div className="aspect-square bg-gray-50 rounded-xl mb-4 overflow-hidden border border-gray-200">
          <img 
            src={previewUrl} 
            alt="Soil Sample Preview" 
            className="w-full h-full object-cover"
          />
        </div>
        <div className="text-center">
          <p className="text-lg font-semibold text-gray-800 mb-2">{selectedFile.name}</p>
          <p className="text-sm text-gray-500">
            Size: {(selectedFile.size / 1024).toFixed(1)} KB
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="space-y-3">
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-bold py-4 px-6 rounded-xl text-lg flex items-center justify-center space-x-3 transition-all duration-300 transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed shadow-lg"
        >
          {loading ? (
            <>
              <Loader className="animate-spin h-6 w-6" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Microscope className="h-6 w-6" />
              <span>Analyze Soil</span>
            </>
          )}
        </button>
        
        <button
          onClick={() => {
            setSelectedFile(null);
            setPreviewUrl(null);
            setPredictionResult(null);
            setError(null);
          }}
          className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-3 px-6 rounded-xl transition-colors"
        >
          Upload Different Image
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50 to-teal-50">
      {/* Header */}
      <header className="text-center py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl flex items-center justify-center mr-4">
              <Leaf className="h-8 w-8 text-white" />
            </div>
            <div className="text-left">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-600 to-teal-700 bg-clip-text text-transparent">
                Soil AI for Tomatoes
              </h1>
              <p className="text-xl text-gray-600">Smart Agriculture Technology</p>
            </div>
          </div>
          <p className="text-lg text-gray-700 max-w-2xl mx-auto">
            Advanced machine learning analysis to optimize your tomato crop yield through precision soil assessment
          </p>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 pb-12">
        <div className="bg-white rounded-3xl shadow-2xl border border-gray-200 overflow-hidden">
          {!selectedFile && !loading && !error && !predictionResult ? (
            renderUploadArea()
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 p-8">
              {/* Left Column */}
              <div className="space-y-6">
                {selectedFile && !predictionResult && !loading && !error ? (
                  renderImagePreview()
                ) : selectedFile && (
                  <div className="bg-gray-50 rounded-2xl p-6">
                    <div className="aspect-square bg-white rounded-xl mb-4 overflow-hidden border border-gray-200">
                      <img 
                        src={previewUrl} 
                        alt="Analyzed Soil Sample" 
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <p className="text-center text-gray-600 font-medium">{selectedFile.name}</p>
                  </div>
                )}
              </div>

              {/* Right Column */}
              <div>
                {loading && renderLoadingState()}
                {error && renderErrorState()}
                {predictionResult && renderResults()}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center py-8 px-4 bg-white border-t border-gray-200">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center mb-4">
            <Sun className="h-5 w-5 text-amber-500 mr-2" />
            <p className="text-gray-600">Empowering sustainable agriculture with AI-driven insights</p>
          </div>
          <p className="text-sm text-gray-500">
            Built with Flask, TensorFlow/Keras, and React.js • © 2025 Soil Analyzer Project
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;