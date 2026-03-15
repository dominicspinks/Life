import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '@environments/environment';
import { map, Observable } from 'rxjs';
import { BudgetBulkImportMapping, BudgetCashFlow, BudgetCategory, BudgetConfiguration, BudgetConfigurationDetails, BudgetDescriptionCategoryRequest, BudgetDescriptionCategoryResponse, BudgetFilter, BudgetPurchase, BudgetPurchaseSummary } from '@core/models/budget.model';
import { PaginatedResponse } from '@core/models/pagination.model';


@Injectable({
    providedIn: 'root'
})
export class BudgetService {
    private http = inject(HttpClient);

    private readonly apiUrl = environment.apiUrl;
    private _selectedYear: Record<number, number> = {};

    getSelectedYear(budgetId: number): number | undefined {
        return this._selectedYear[budgetId];
    }

    setSelectedYear(budgetId: number, year: number | undefined): void {
        if (year) {
            this._selectedYear[budgetId] = year;
        } else {
            delete this._selectedYear[budgetId];
        }
    }

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
        return this.http.post<BudgetConfiguration>(`${this.apiUrl}/budgets/${budgetId}/categories/${categoryId}/reorder/`, { new_order: newOrder });
    }

    getPurchases(id: number, filters?: BudgetFilter): Observable<PaginatedResponse<BudgetPurchase> | BudgetPurchase[]> {
        const filterList: string[] = [];
        let searchFilters = '';
        if (filters) {
            searchFilters += '?';

            if (filters.get_all) {
                filterList.push('get_all=true');
            }
            if (filters.ordering) {
                filterList.push(`ordering=${filters.ordering.join(',')}`);
            }
            if (filters.category && filters.category.length > 0) {
                for (let cat of filters.category) {
                    filterList.push(`category=${cat}`);
                }
            }
            if (filters.page) {
                filterList.push(`page=${filters.page}`);
            }
            if (filters.description) {
                filterList.push(`description=${encodeURIComponent(filters.description)}`);
            }
            if (filters.purchase_date__year) {
                filterList.push(`purchase_date__year=${filters.purchase_date__year}`);
            }
            if (filterList.length > 0) {
                searchFilters += filterList.join('&');
            }
        }
        return this.http.get<any>(`${this.apiUrl}/budgets/${id}/purchases/${searchFilters}`).pipe(
            map(response => {
                // If get_all is true, it returns an array
                if (Array.isArray(response)) {
                    return response.map(this.parsePurchaseResponse.bind(this));
                }
                // Otherwise it's paginated
                return {
                    ...response,
                    results: response.results.map(this.parsePurchaseResponse.bind(this))
                };
            })
        );
    }

    deletePurchase(budgetId: number, purchaseId: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/budgets/${budgetId}/purchases/${purchaseId}/`);
    }

    addPurchase(budgetId: number, purchase: BudgetPurchase): Observable<BudgetPurchase> {
        return this.http.post<BudgetPurchase>(`${this.apiUrl}/budgets/${budgetId}/purchases/`, this.formatPurchaseForRequest(purchase)).pipe(
            map(this.parsePurchaseResponse));
    }

    updatePurchase(budgetId: number, purchaseId: number, purchase: BudgetPurchase): Observable<BudgetPurchase> {
        return this.http.patch<BudgetPurchase>(
            `${this.apiUrl}/budgets/${budgetId}/purchases/${purchaseId}/`,
            this.formatPurchaseForRequest(purchase)).pipe(
                map(this.parsePurchaseResponse));
    }

    addBulkPurchase(budgetId: number, purchases: BudgetPurchase[]): Observable<BudgetPurchase[]> {
        return this.http.post<BudgetPurchase[]>(`${this.apiUrl}/budgets/${budgetId}/purchases/bulk/`, purchases.map(purchase => this.formatPurchaseForRequest(purchase))).pipe(
            map(purchases => purchases.map(this.parsePurchaseResponse)));
    }

    getPurchaseSummary(budgetId: number, start_date: string, end_date: string): Observable<BudgetPurchaseSummary[]> {
        return this.http.get<BudgetPurchaseSummary[]>(`${this.apiUrl}/budgets/${budgetId}/summary/?start_date=${start_date}&end_date=${end_date}`);
    }

    getBudgetYears(budgetId: number): Observable<number[]> {
        return this.http.get<number[]>(`${this.apiUrl}/budgets/${budgetId}/summary/years/`);
    }

    private formatPurchaseForRequest(p: BudgetPurchase): any {
        return {
            ...p,
            purchase_date: p.purchase_date.toISOString().split('T')[0]
        };
    }

    private parsePurchaseResponse(p: any): BudgetPurchase {
        return {
            ...p,
            purchase_date: new Date(p.purchase_date)
        };
    }

    getCashFlows(budgetId: number): Observable<BudgetCashFlow[]> {
        return this.http.get<BudgetCashFlow[]>(`${this.apiUrl}/budgets/${budgetId}/cashflows/`);
    }

    addCashFlow(budgetId: number, cashFlow: BudgetCashFlow): Observable<BudgetCashFlow> {
        return this.http.post<BudgetCashFlow>(`${this.apiUrl}/budgets/${budgetId}/cashflows/`, cashFlow);
    }

    updateCashFlow(budgetId: number, cashFlowId: number, cashFlow: BudgetCashFlow): Observable<BudgetCashFlow> {
        return this.http.patch<BudgetCashFlow>(`${this.apiUrl}/budgets/${budgetId}/cashflows/${cashFlowId}/`, cashFlow);
    }

    deleteCashFlow(budgetId: number, cashFlowId: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/budgets/${budgetId}/cashflows/${cashFlowId}/`);
    }

    getDescriptionCategories(budgetId: number, descriptions: BudgetDescriptionCategoryRequest[]): Observable<BudgetDescriptionCategoryResponse[]> {
        return this.http.post<BudgetDescriptionCategoryResponse[]>(`${this.apiUrl}/budgets/${budgetId}/purchases/analyse/`, descriptions);
    }

    getBulkImportMappings(budgetId: number): Observable<BudgetBulkImportMapping[]> {
        return this.http.get<BudgetBulkImportMapping[]>(`${this.apiUrl}/budgets/${budgetId}/purchases/mappings/`);
    }

    saveBulkImportMapping(budgetId: number, mapping: BudgetBulkImportMapping): Observable<BudgetBulkImportMapping> {
        return this.http.post<BudgetBulkImportMapping>(`${this.apiUrl}/budgets/${budgetId}/purchases/mappings/`, mapping);
    }
}
