export interface UserModule {
    id: number;
    module: number;
    module_name: string;
    name: string;
    order: number;
    is_enabled: boolean;
    is_read_only: boolean;
    is_checkable: boolean;
    created_at: Date;
    modified_at: Date;
}

export interface CreateUserModule {
    module: number;
    name: string;
    order: number;
    is_enabled: boolean;
    is_read_only: boolean;
    is_checkable: boolean;
}

export interface UserModuleMenu {
    id: number;
    module_name: string;
    route: string;
}