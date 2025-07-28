'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/Button';
import { apiClient } from '@/lib/api';
import { ViolationCreate } from '@/types';
import { 
  Camera, 
  MapPin, 
  Upload, 
  X, 
  AlertCircle,
  CheckCircle
} from 'lucide-react';

const violationSchema = z.object({
  description: z.string().min(10, 'Description must be at least 10 characters').max(2000, 'Description must be less than 2000 characters'),
  hoa: z.string().min(1, 'HOA is required'),
  address: z.string().min(2, 'Address must be at least 2 characters').max(100, 'Address must be less than 100 characters'),
  location: z.string().min(2, 'Location must be at least 2 characters').max(100, 'Location must be less than 100 characters'),
  offender: z.string().min(2, 'Offender must be at least 2 characters').max(100, 'Offender must be less than 100 characters'),
  violation_type: z.string().optional(),
  gps_coordinates: z.string().optional(),
});

type ViolationFormData = z.infer<typeof violationSchema>;

interface ViolationFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export default function ViolationForm({ onSuccess, onCancel }: ViolationFormProps) {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [gpsCoordinates, setGpsCoordinates] = useState<string>('');
  const [gpsLoading, setGpsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<ViolationFormData>({
    resolver: zodResolver(violationSchema),
  });

  const handlePhotoUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        setError('Photo must be less than 5MB');
        return;
      }
      
      setPhotoFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setPhotoPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
      setError(null);
    }
  };

  const handleCameraCapture = () => {
    cameraInputRef.current?.click();
  };

  const handleFileUpload = () => {
    fileInputRef.current?.click();
  };

  const removePhoto = () => {
    setPhotoFile(null);
    setPhotoPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  const getCurrentLocation = () => {
    setGpsLoading(true);
    setError(null);

    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser');
      setGpsLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        const coords = `${latitude},${longitude}`;
        setGpsCoordinates(coords);
        setValue('gps_coordinates', coords);
        setGpsLoading(false);
      },
      (error) => {
        console.error('GPS Error:', error);
        setError('Failed to get location. Please check your GPS settings.');
        setGpsLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000, // 5 minutes
      }
    );
  };

  const onSubmit = async (data: ViolationFormData) => {
    try {
      setIsSubmitting(true);
      setError(null);

      const violationData: ViolationCreate = {
        ...data,
        file: photoFile || undefined,
        gps_coordinates: gpsCoordinates || undefined,
        mobile_capture: !!photoFile,
        auto_gps: !!gpsCoordinates,
      };

      await apiClient.createViolation(violationData);
      
      setSuccess(true);
      setTimeout(() => {
        onSuccess?.();
        router.push('/dashboard/violations');
      }, 2000);
    } catch (error) {
      console.error('Failed to create violation:', error);
      setError(error instanceof Error ? error.message : 'Failed to create violation');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
          <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Success!</h2>
          <p className="text-gray-600">Violation has been created successfully.</p>
          <p className="text-sm text-gray-500 mt-2">Redirecting to violations page...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-semibold text-gray-900">
                Report New Violation
              </h1>
              {onCancel && (
                <Button
                  variant="ghost"
                  onClick={onCancel}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
            {/* Error/Success Messages */}
            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <div className="flex">
                  <AlertCircle className="h-5 w-5 text-red-400" />
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">
                      Error
                    </h3>
                    <div className="mt-2 text-sm text-red-700">
                      {error}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Violation Description *
              </label>
              <textarea
                id="description"
                rows={4}
                className={`w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500 ${
                  errors.description ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Describe the violation in detail..."
                {...register('description')}
              />
              {errors.description && (
                <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
              )}
            </div>

            {/* HOA */}
            <div>
              <label htmlFor="hoa" className="block text-sm font-medium text-gray-700 mb-2">
                HOA *
              </label>
              <input
                type="text"
                id="hoa"
                className={`w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500 ${
                  errors.hoa ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="HOA #001"
                {...register('hoa')}
              />
              {errors.hoa && (
                <p className="mt-1 text-sm text-red-600">{errors.hoa.message}</p>
              )}
            </div>

            {/* Address and Location */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
                  Property Address *
                </label>
                <input
                  type="text"
                  id="address"
                  className={`w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500 ${
                    errors.address ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="123 Main St, Unit 5"
                  {...register('address')}
                />
                {errors.address && (
                  <p className="mt-1 text-sm text-red-600">{errors.address.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
                  Specific Location *
                </label>
                <input
                  type="text"
                  id="location"
                  className={`w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500 ${
                    errors.location ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Front yard, Back porch, etc."
                  {...register('location')}
                />
                {errors.location && (
                  <p className="mt-1 text-sm text-red-600">{errors.location.message}</p>
                )}
              </div>
            </div>

            {/* Offender and Violation Type */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="offender" className="block text-sm font-medium text-gray-700 mb-2">
                  Resident/Offender *
                </label>
                <input
                  type="text"
                  id="offender"
                  className={`w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500 ${
                    errors.offender ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="John Smith"
                  {...register('offender')}
                />
                {errors.offender && (
                  <p className="mt-1 text-sm text-red-600">{errors.offender.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="violation_type" className="block text-sm font-medium text-gray-700 mb-2">
                  Violation Type
                </label>
                <select
                  id="violation_type"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  {...register('violation_type')}
                >
                  <option value="">Select type...</option>
                  <option value="landscaping">Landscaping</option>
                  <option value="parking">Parking</option>
                  <option value="noise">Noise</option>
                  <option value="trash">Trash/Recycling</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="pets">Pets</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            {/* GPS Coordinates */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                GPS Coordinates
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="37.7749,-122.4194"
                  value={gpsCoordinates}
                  onChange={(e) => {
                    setGpsCoordinates(e.target.value);
                    setValue('gps_coordinates', e.target.value);
                  }}
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={getCurrentLocation}
                  loading={gpsLoading}
                >
                  <MapPin className="h-4 w-4 mr-2" />
                  Get Location
                </Button>
              </div>
              <p className="mt-1 text-xs text-gray-500">
                Automatically capture your current location or enter coordinates manually
              </p>
            </div>

            {/* Photo Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Photo Evidence
              </label>
              
              {photoPreview ? (
                <div className="space-y-4">
                  <div className="relative">
                    <img
                      src={photoPreview}
                      alt="Violation preview"
                      className="w-full h-64 object-cover rounded-lg border border-gray-300"
                    />
                    <button
                      type="button"
                      onClick={removePhoto}
                      className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex space-x-2">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleCameraCapture}
                    >
                      <Camera className="h-4 w-4 mr-2" />
                      Take Photo
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleFileUpload}
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Photo
                    </Button>
                  </div>
                  <p className="text-xs text-gray-500">
                    Take a photo with your camera or upload an existing image (max 5MB)
                  </p>
                </div>
              )}

              {/* Hidden file inputs */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handlePhotoUpload}
                className="hidden"
              />
              <input
                ref={cameraInputRef}
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handlePhotoUpload}
                className="hidden"
              />
            </div>

            {/* Submit Buttons */}
            <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
              {onCancel && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={onCancel}
                >
                  Cancel
                </Button>
              )}
              <Button
                type="submit"
                loading={isSubmitting}
              >
                {isSubmitting ? 'Creating...' : 'Create Violation'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
} 