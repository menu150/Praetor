'use client';
import { Component } from 'react';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('UI Error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return <div className="text-red-600 p-4">Something went wrong: {this.state.error.message}</div>;
    }

    return this.props.children;
  }
}
