import { UserModule } from "./userModule.model";

export interface BudgetCategory {
    id?: number;
    name: string;
    weekly_target: number;
    excluded_from_budget: boolean;
    order: number;
    is_enabled: boolean;
}

export interface BudgetConfiguration extends UserModule {
    categories: BudgetCategory[]
}

export type BudgetConfigurationDetails = Pick<
    UserModule,
    'id' | 'name' | 'order' | 'is_enabled' | 'is_read_only'
>;

export interface BudgetPurchase {
    id?: number;
    purchase_date: Date;
    amount: number;
    description: string;
    category: number | null;
    category_name?: string;
}

export interface BudgetFilter {
    get_all?: boolean,
    ordering?: ('purchase_date' | 'amount' | 'category__name')[],
    category?: number[]
}

export interface BudgetPurchaseSummary {
    week: number;
    category: number;
    total: number;
}

export interface BudgetCashFlow {
    id?: number;
    amount: number;
    description: string;
    is_income: boolean;
    period: number;
    period_name?: string;
}

export interface BudgetDescriptionCategoryRequest {
    index: number;
    description: string;
}

export interface BudgetDescriptionCategoryResponse {
    index: number;
    category: number;
}