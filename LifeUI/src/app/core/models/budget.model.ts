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
    purchase_date: string;
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