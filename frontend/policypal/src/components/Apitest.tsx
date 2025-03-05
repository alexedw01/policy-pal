'use client';
import { useEffect, useState } from 'react';
import { testConnection } from '@/lib/api';

export default function ApiTest() {
    const [status, setStatus] = useState<string>('Testing...');

    useEffect(() => {
        async function test() {
            try {
                const result = await testConnection();
                setStatus(result ? 'Connected' : 'Failed');
            } catch (error) {
                setStatus('Error: ' + (error as Error).message);
            }
        }
        test();
    }, []);

    return (
        <div className="p-4 bg-gray-100 rounded">
            <p>API Status: {status}</p>
        </div>
    );
}