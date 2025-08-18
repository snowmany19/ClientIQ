import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { ContractRecord, ContractCreate } from '@/types';

// Query keys for better cache management
export const contractKeys = {
  all: ['contracts'] as const,
  lists: () => [...contractKeys.all, 'list'] as const,
  list: (filters: string) => [...contractKeys.lists(), { filters }] as const,
  details: () => [...contractKeys.all, 'detail'] as const,
  detail: (id: number) => [...contractKeys.details(), id] as const,
};

// Hook for fetching contracts
export function useContracts() {
  return useQuery({
    queryKey: contractKeys.lists(),
    queryFn: async () => {
      const response = await apiClient.getContracts({
        page: 1,
        per_page: 20
      });
      // Backend returns ContractRecordList with contracts array directly
      return response.contracts || [];
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

// Hook for fetching a single contract
export function useContract(id: number) {
  return useQuery({
    queryKey: contractKeys.detail(id),
    queryFn: async () => {
      const response = await apiClient.getContract(id);
      return response;
    },
    enabled: !!id,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

// Hook for creating a contract
export function useCreateContract() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (contractData: ContractCreate) => {
      return await apiClient.createContract(contractData);
    },
    onSuccess: () => {
      // Invalidate and refetch contracts list
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}

// Hook for updating a contract
export function useUpdateContract() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<ContractRecord> }) => {
      return await apiClient.updateContract(id, data);
    },
    onSuccess: (data, variables) => {
      // Update the specific contract in cache
      queryClient.setQueryData(contractKeys.detail(variables.id), data);
      // Invalidate contracts list
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}

// Hook for deleting a contract
export function useDeleteContract() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      return await apiClient.deleteContract(id);
    },
    onSuccess: (_, id) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: contractKeys.detail(id) });
      // Invalidate contracts list
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}

// Hook for analyzing a contract
export function useAnalyzeContract() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      return await apiClient.analyzeContract(id);
    },
    onSuccess: (_, id) => {
      // Invalidate the specific contract to refetch with analysis results
      queryClient.invalidateQueries({ queryKey: contractKeys.detail(id) });
      // Invalidate contracts list to update status
      queryClient.invalidateQueries({ queryKey: contractKeys.lists() });
    },
  });
}
