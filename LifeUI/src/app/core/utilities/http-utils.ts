import { map, OperatorFunction } from 'rxjs';
import { PaginatedResponse } from '../models/pagination.model';

export function normalisePaginatedResponse<T>(): OperatorFunction<T[] | PaginatedResponse<T>, PaginatedResponse<T>> {
    return map((response): PaginatedResponse<T> => {
        if (Array.isArray(response)) {
            return {
                count: response.length,
                next: null,
                previous: null,
                results: response
            };
        }
        return response;
    });
}