export interface FieldTypeRule {
    id: number;
    rule: string
}

export interface FieldType {
    id: number;
    name: string;
    rules?: FieldTypeRule[]
}