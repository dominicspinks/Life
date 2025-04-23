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

export type CreateUserModule = Pick<
    UserModule,
    'module' | 'name' | 'order' | 'is_enabled' | 'is_read_only' | 'is_checkable'
>;



export type UserModuleMenu = Pick<UserModule,
    'id' | 'name'>