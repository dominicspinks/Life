import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@environments/environment';
import { CreateUserModule, UserModule } from '@core/models/userModule.model';
import { ModuleType } from '@core/models/moduleType.model';
import { PaginatedResponse } from '@core/models/pagination.model';
import { normalisePaginatedResponse } from '@core/utilities/http-utils';

@Injectable({
    providedIn: 'root'
})
export class ModuleService {
    private http = inject(HttpClient);

    private readonly apiUrl = environment.apiUrl;

    getUserModules(getAll = false): Observable<PaginatedResponse<UserModule>> {
        const params: Record<string, string> = getAll ? { get_all: 'true' } : {};

        return this.http
            .get<UserModule[] | PaginatedResponse<UserModule>>(
                `${this.apiUrl}/modules/user-modules/`,
                { params }
            )
            .pipe(normalisePaginatedResponse<UserModule>());
    }

    getModuleTypes(): Observable<ModuleType[]> {
        return this.http.get<ModuleType[]>(`${this.apiUrl}/modules/types/?get_all=true`);
    }

    addModule(module: CreateUserModule): Observable<UserModule> {
        return this.http.post<UserModule>(`${this.apiUrl}/modules/user-modules/`, module);
    }

    deleteModule(moduleId: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/modules/user-modules/${moduleId}/`);
    }
}
