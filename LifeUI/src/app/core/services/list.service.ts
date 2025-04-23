import { inject, Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { ListConfiguration, ListConfigurationDetails, ListField } from '../models/list.model';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class ListService {
    private http = inject(HttpClient);

    private readonly apiUrl = environment.apiUrl;

    getModule(id: number): Observable<ListConfiguration> {
        return this.http.get<ListConfiguration>(`${this.apiUrl}/lists/configurations/${id}/`);
    }

    updateModuleDetails(details: ListConfigurationDetails): Observable<ListConfiguration> {
        return this.http.patch<ListConfiguration>(`${this.apiUrl}/lists/configurations/${details.id}/`, details);
    }

    addField(configurationId: number, field: ListField): Observable<ListField> {
        return this.http.post<ListField>(`${this.apiUrl}/lists/configurations/${configurationId}/fields/`, field);
    }

    updateField(configurationId: number, fieldId: number, field: ListField): Observable<ListField> {
        return this.http.patch<ListField>(`${this.apiUrl}/lists/configurations/${configurationId}/fields/${fieldId}/`, field);
    }

    deleteField(configurationId: number, fieldId: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/lists/configurations/${configurationId}/fields/${fieldId}/`);
    }
}
