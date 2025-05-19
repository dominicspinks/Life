import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';
import { Observable } from 'rxjs';
import { BudgetCategory, BudgetConfiguration, BudgetConfigurationDetails } from '../models/budget.model';

@Injectable({
    providedIn: 'root'
})
export class BudgetService {
    private http = inject(HttpClient);

    private readonly apiUrl = environment.apiUrl;

    getBudgetConfiguration(id: number): Observable<BudgetConfiguration> {
        return this.http.get<BudgetConfiguration>(`${this.apiUrl}/budgets/${id}/`);
    }

    updateBudgetDetails(details: BudgetConfigurationDetails): Observable<BudgetConfiguration> {
        return this.http.patch<BudgetConfiguration>(`${this.apiUrl}/budgets/${details.id}/`, details);
    }

    addCategory(budgetId: number, category: BudgetCategory): Observable<BudgetCategory> {
        return this.http.post<BudgetCategory>(`${this.apiUrl}/budgets/${budgetId}/categories/`, category);
    }

    updateCategory(budgetId: number, categoryId: number, category: BudgetCategory): Observable<BudgetCategory> {
        return this.http.patch<BudgetCategory>(`${this.apiUrl}/budgets/${budgetId}/categories/${categoryId}/`, category);
    }

    deleteCategory(budgetId: number, categoryId: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/budgets/${budgetId}/categories/${categoryId}/`);
    }

    reorderCategories(budgetId: number, categoryId: number, newOrder: number): Observable<BudgetConfiguration> {
        // Replace with the actual API endpoint for reordering categories
        return this.http.post<BudgetConfiguration>(`${this.apiUrl}/budgets/${budgetId}/categories/${categoryId}/reorder/`, { new_order: newOrder });
    }

}
