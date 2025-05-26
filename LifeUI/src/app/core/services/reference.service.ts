import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '@environments/environment';
import { FieldType } from '@core/models/fieldType.model';

@Injectable({
    providedIn: 'root'
})
export class ReferenceService {
    private http = inject(HttpClient);

    private readonly apiUrl = environment.apiUrl;

    getFieldTypes(): Observable<FieldType[]> {
        return this.http.get<FieldType[]>(`${this.apiUrl}/reference/field-types/`);
    }

    getFieldTypesWithRules(): Observable<FieldType[]> {
        return this.http.get<FieldType[]>(`${this.apiUrl}/reference/field-types/?detailed=true`);
    }
}
