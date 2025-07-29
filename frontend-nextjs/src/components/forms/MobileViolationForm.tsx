'use client';

import { useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { apiClient } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { 
  Camera, 
  MapPin, 
  Upload, 
  X,
  AlertCircle,
  CheckCircle,
  ArrowLeft,
  ArrowRight
} from 'lucide-react';
import Image from 'next/image';

const violationSchema = z.object({
  description: z.string().min(10, 'Description must be at least 10 characters').max(2000, 'Description must be less than 2000 characters'),
  hoa: z.string().min(1, 'HOA is required'),
  address: z.string().min(1, 'Address is required'),
  location: z.string().min(1, 'Location is required'),
  offender: z.string().min(1, 'Offender is required'),
  gps_coordinates: z.string().optional(),
  violation_type: z.string().optional(),
});

type ViolationFormData = z.infer<typeof violationSchema>;

interface MobileViolationFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

export default function MobileViolationForm({ onSuccess, onCancel }: MobileViolationFormProps) {
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [gpsLocation, setGpsLocation] = useState<{ lat: number; lng: number } | null>(null);
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

  const totalSteps = 4;

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const capturePhoto = () => {
    cameraInputRef.current?.click();
  };

  const uploadPhoto = () => {
    fileInputRef.current?.click();
  };

  const handlePhotoChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPhotoPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setGpsLocation({ lat: latitude, lng: longitude });
          setValue('gps_coordinates', `${latitude},${longitude}`);
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    }
  };

  const onSubmit = async (data: ViolationFormData) => {
    setIsSubmitting(true);
    try {
      // Handle form submission
      await apiClient.createViolation(data);
      onSuccess?.();
    } catch (error) {
      console.error('Failed to create violation:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Violation Details</h3>
            
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Description *
              </label>
              <textarea
                {...register('description')}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Describe the violation in detail..."
              />
              {errors.description && (
                <p className="mt-1 text-sm text-red-700 font-medium">{errors.description.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Violation Type
              </label>
              <select
                {...register('violation_type')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select type...</option>
                <option value="parking">Parking Violation</option>
                <option value="noise">Noise Violation</option>
                <option value="maintenance">Maintenance Issue</option>
                <option value="trash">Trash/Recycling</option>
                <option value="pet">Pet Violation</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Evidence & Photos</h3>
            
            <div className="space-y-3">
              <Button
                type="button"
                onClick={capturePhoto}
                className="w-full flex items-center justify-center space-x-2"
              >
                <Camera className="h-5 w-5" />
                <span>Take Photo</span>
              </Button>
              
              <Button
                type="button"
                variant="outline"
                onClick={uploadPhoto}
                className="w-full flex items-center justify-center space-x-2"
              >
                <Upload className="h-5 w-5" />
                <span>Upload Photo</span>
              </Button>
            </div>

            {photoPreview && (
              <div className="relative">
                <Image
                  src={photoPreview}
                  alt="Violation preview"
                  width={400}
                  height={300}
                  className="w-full h-48 object-cover rounded-lg border border-gray-300"
                />
                <button
                  type="button"
                  onClick={() => setPhotoPreview(null)}
                  className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handlePhotoChange}
              className="hidden"
            />
            <input
              ref={cameraInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handlePhotoChange}
              className="hidden"
            />
          </div>
        );

      case 3:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Location & GPS</h3>
            
            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Address *
              </label>
              <input
                {...register('address')}
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter property address"
              />
              {errors.address && (
                <p className="mt-1 text-sm text-red-700 font-medium">{errors.address.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                Location Description *
              </label>
              <input
                {...register('location')}
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Front yard, Back patio, etc."
              />
              {errors.location && (
                <p className="mt-1 text-sm text-red-700 font-medium">{errors.location.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-900 mb-2">
                GPS Coordinates
              </label>
              <div className="flex space-x-2">
                <input
                  {...register('gps_coordinates')}
                  type="text"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-gray-900 bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Latitude, Longitude"
                  readOnly
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={getCurrentLocation}
                  className="flex items-center space-x-1"
                >
                  <MapPin className="h-4 w-4" />
                  <span>GPS</span>
                </Button>
              </div>
              {gpsLocation && (
                <p className="mt-1 text-sm text-green-600 font-medium">
                  Location captured: {gpsLocation.lat.toFixed(6)}, {gpsLocation.lng.toFixed(6)}
                </p>
              )}
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Review & Submit</h3>
            
            <div className="bg-gray-50 rounded-lg p-4 space-y-3">
              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  Offender *
                </label>
                <input
                  {...register('offender')}
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter offender name or unit number"
                />
                {errors.offender && (
                  <p className="mt-1 text-sm text-red-700 font-medium">{errors.offender.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  HOA *
                </label>
                <input
                  {...register('hoa')}
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900 bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter HOA name"
                />
                {errors.hoa && (
                  <p className="mt-1 text-sm text-red-700 font-medium">{errors.hoa.message}</p>
                )}
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-blue-900 mb-2">Summary</h4>
              <div className="text-sm text-blue-800 space-y-1">
                <p>• Violation type: {watch('violation_type') || 'Not specified'}</p>
                <p>• Address: {watch('address') || 'Not specified'}</p>
                <p>• Photo: {photoPreview ? 'Attached' : 'Not attached'}</p>
                <p>• GPS: {gpsLocation ? 'Captured' : 'Not captured'}</p>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="px-4 py-3 flex items-center justify-between">
          <button
            type="button"
            onClick={onCancel}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="h-5 w-5" />
            <span>Cancel</span>
          </button>
          
          <div className="flex items-center space-x-2">
            {Array.from({ length: totalSteps }).map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full ${
                  index + 1 <= currentStep ? 'bg-blue-600' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>
          
          <div className="text-sm text-gray-500">
            {currentStep} of {totalSteps}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {renderStep()}

          {/* Navigation */}
          <div className="flex space-x-3 pt-4">
            {currentStep > 1 && (
              <Button
                type="button"
                variant="outline"
                onClick={prevStep}
                className="flex-1"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Previous
              </Button>
            )}
            
            {currentStep < totalSteps ? (
              <Button
                type="button"
                onClick={nextStep}
                className="flex-1"
              >
                Next
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            ) : (
              <Button
                type="submit"
                loading={isSubmitting}
                className="flex-1"
              >
                Submit Violation
              </Button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
} 