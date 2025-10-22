import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://lindia-b-production.up.railway.app';
const AI_ENGINE_URL = process.env.NEXT_PUBLIC_AI_ENGINE_URL || 'https://lindia-ai-production.up.railway.app';

export async function GET(request: NextRequest) {
  try {
    // Check backend health
    const backendResponse = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Check AI engine health
    const aiResponse = await fetch(`${AI_ENGINE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const backendHealth = backendResponse.ok ? await backendResponse.json() : { status: 'error' };
    const aiHealth = aiResponse.ok ? await aiResponse.json() : { status: 'error' };

    return NextResponse.json({
      frontend: { status: 'healthy', timestamp: new Date().toISOString() },
      backend: backendHealth,
      ai_engine: aiHealth,
      overall_status: backendResponse.ok && aiResponse.ok ? 'healthy' : 'degraded'
    });
  } catch (error) {
    console.error('Health check error:', error);
    return NextResponse.json(
      { 
        frontend: { status: 'healthy', timestamp: new Date().toISOString() },
        backend: { status: 'error' },
        ai_engine: { status: 'error' },
        overall_status: 'degraded',
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 200 }
    );
  }
}
