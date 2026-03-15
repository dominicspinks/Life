import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '@environments/environment';

@Injectable({
    providedIn: 'root'
})
export class ProfileService {
    private http = inject(HttpClient);

    private readonly apiUrl = environment.apiUrl;

    deleteProfile(): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/profile/delete/`);
    }
}
