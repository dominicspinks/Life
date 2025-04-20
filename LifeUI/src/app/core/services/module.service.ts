import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Observable } from 'rxjs';
import { CreateUserModule, UserModule } from '../models/userModule.model';
import { ModuleType } from '../models/moduleType.model';

interface UserModulesResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: UserModule[];
}

interface ModuleTypeResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: ModuleType[];
}

@Injectable({
    providedIn: 'root'
})
export class ModuleService {
    private readonly apiUrl = environment.apiUrl;

    constructor(private http: HttpClient) { }

    getUserModules(): Observable<UserModulesResponse> {
        return this.http.get<UserModulesResponse>(`${this.apiUrl}/modules/user-modules/`);
    }

    getModuleTypes(): Observable<ModuleTypeResponse> {
        return this.http.get<ModuleTypeResponse>(`${this.apiUrl}/modules/types/`);
    }

    addModule(module: CreateUserModule): Observable<UserModule> {
        return this.http.post<UserModule>(`${this.apiUrl}/modules/user-modules/`, module);
    }

    deleteModule(moduleId: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/modules/user-modules/${moduleId}/`);
    }
}
