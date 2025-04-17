import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Observable } from 'rxjs';
import { UserModule } from '../models/userModule.model';
import { ModuleType } from '../models/moduleType.model';

interface UserModulesResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: UserModule[];
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

    getModuleTypes(): Observable<ModuleType[]> {
        return this.http.get<ModuleType[]>(`${this.apiUrl}/modules/types/`);
    }
}
