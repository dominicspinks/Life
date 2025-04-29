import { inject, Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { ListConfiguration, ListConfigurationDetails, ListField, ListItem } from '../models/list.model';
import { Observable } from 'rxjs';
import { PaginatedResponse } from '../models/pagination.model';

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

    getListData(id: number): Observable<PaginatedResponse<ListItem>> {
        return this.http.get<PaginatedResponse<ListItem>>(`${this.apiUrl}/lists/data/${id}/items/`);
    }

    getListDataByUrl(url: string): Observable<PaginatedResponse<ListItem>> {
        return this.http.get<PaginatedResponse<ListItem>>(url);
    }

    getListDataByPage(id: number, page: number): Observable<PaginatedResponse<ListItem>> {
        return this.http.get<PaginatedResponse<ListItem>>(`${this.apiUrl}/lists/data/${id}/items/?page=${page}`);
    }

    updateListItemCompletion(listId: number, itemId: number, isCompleted: boolean): Observable<ListItem> {
        return this.http.patch<ListItem>(`${this.apiUrl}/lists/data/${listId}/items/${itemId}/`, {
            is_completed: isCompleted
        });
    }

    addListItem(listId: number, item: ListItem): Observable<ListItem> {
        return this.http.post<ListItem>(`${this.apiUrl}/lists/data/${listId}/items/`, item);
    }

    deleteListItem(listId: number, itemId: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/lists/data/${listId}/items/${itemId}/`);
    }

    updateListItem(listId: number, item: ListItem): Observable<ListItem> {
        return this.http.patch<ListItem>(`${this.apiUrl}/lists/data/${listId}/items/${item.id}/`, item);
    }
}
