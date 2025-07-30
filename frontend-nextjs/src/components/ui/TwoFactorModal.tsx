'use client';

import { useState } from 'react';
import { Button } from './Button';
import { X, Copy, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';

interface TwoFactorModalProps {
  isOpen: boolean;
  onClose: () => void;
  qrCode: string;
  secret: string;
  onVerify: (code: string) => Promise<boolean>;
}

export function TwoFactorModal({ isOpen, onClose, qrCode, secret, onVerify }: TwoFactorModalProps) {
  const [verificationCode, setVerificationCode] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleVerify = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setVerificationStatus('error');
      return;
    }

    setIsVerifying(true);
    setVerificationStatus('idle');

    try {
      const success = await onVerify(verificationCode);
      if (success) {
        setVerificationStatus('success');
        setTimeout(() => {
          onClose();
          setVerificationCode('');
          setVerificationStatus('idle');
        }, 2000);
      } else {
        setVerificationStatus('error');
      }
    } catch (error) {
      setVerificationStatus('error');
    } finally {
      setIsVerifying(false);
    }
  };

  const copySecret = () => {
    navigator.clipboard.writeText(secret);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const generateNewSecret = () => {
    // This would typically call the backend to generate a new secret
    window.location.reload();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Set Up Two-Factor Authentication</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="space-y-4">
          <div className="text-sm text-gray-600">
            <p className="mb-3">Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.):</p>
          </div>

          <div className="flex justify-center">
            <div className="bg-gray-50 p-4 rounded-lg">
              <img 
                src={qrCode} 
                alt="2FA QR Code" 
                className="w-48 h-48"
              />
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Secret Key:</span>
              <div className="flex items-center space-x-2">
                <code className="text-xs bg-gray-100 px-2 py-1 rounded font-mono">
                  {secret}
                </code>
                <button
                  onClick={copySecret}
                  className="text-blue-600 hover:text-blue-800"
                  title="Copy secret"
                >
                  {copied ? <CheckCircle className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                </button>
              </div>
            </div>
            
            <button
              onClick={generateNewSecret}
              className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              Generate new secret
            </button>
          </div>

          <div className="border-t pt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Verification Code
            </label>
            <input
              type="text"
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-center text-lg font-mono tracking-widest"
              placeholder="000000"
              maxLength={6}
            />
            
            {verificationStatus === 'error' && (
              <div className="flex items-center text-red-600 text-sm mt-2">
                <AlertCircle className="h-4 w-4 mr-1" />
                Invalid verification code
              </div>
            )}
            
            {verificationStatus === 'success' && (
              <div className="flex items-center text-green-600 text-sm mt-2">
                <CheckCircle className="h-4 w-4 mr-1" />
                Verification successful! 2FA is now enabled.
              </div>
            )}
          </div>

          <div className="flex space-x-3 pt-4">
            <Button
              onClick={handleVerify}
              disabled={isVerifying || verificationCode.length !== 6}
              className="flex-1"
            >
              {isVerifying ? 'Verifying...' : 'Verify & Enable 2FA'}
            </Button>
            <Button
              variant="outline"
              onClick={onClose}
              className="flex-1"
            >
              Cancel
            </Button>
          </div>

          <div className="text-xs text-gray-500 space-y-1">
            <p>• Install an authenticator app if you haven't already</p>
            <p>• Scan the QR code or manually enter the secret key</p>
            <p>• Enter the 6-digit code from your app to verify</p>
          </div>
        </div>
      </div>
    </div>
  );
} 