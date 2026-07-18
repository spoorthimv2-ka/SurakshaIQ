import React from 'react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md w-full space-y-8">
            <div>
              <h2 className="text-center text-2xl font-bold text-gray-900">
                Something went wrong
              </h2>
              <p className="mt-4 text-center text-gray-600">
                We're sorry, but something unexpected happened. Please try refreshing the page.
              </p>
              {import.meta.env.DEV && this.state.error && (
                <pre className="mt-4 p-4 bg-red-50 text-red-800 text-xs rounded overflow-auto">
                  {this.state.error.toString()}
                </pre>
              )}
              <button
                onClick={() => window.location.reload()}
                className="mt-6 w-full bg-navy-600 text-white px-4 py-2 rounded-lg hover:bg-navy-700 transition-colors"
              >
                Refresh Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
