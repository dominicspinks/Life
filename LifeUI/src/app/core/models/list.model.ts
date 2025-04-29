import { FieldTypeRule } from "./fieldType.model";
import { UserModule } from "./userModule.model";

export interface ListFieldRule {
    id?: number
    field_type_rule: FieldTypeRule
}

export interface ListFieldOption {
    id?: number
    option_name: string
}

export interface ListField {
    id?: number
    user_module: number
    field_name: string
    field_type: number
    field_type_name?: string
    is_mandatory: boolean
    order: number
    rules: ListFieldRule[]
    options: ListFieldOption[]
}

export interface ListConfiguration extends UserModule {
    list_fields: ListField[]
}

export interface ListConfigurationDetails {
    id: number;
    name: string;
    order: number;
    is_enabled: boolean;
    is_read_only: boolean;
    is_checkable: boolean;
}

export interface ListItemField {
    field: number;
    value: string;
}

export interface ListItem {
    id?: number
    user_module: number
    is_completed: boolean
    modified_at?: Date
    field_values: ListItemField[]
}