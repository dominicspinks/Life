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