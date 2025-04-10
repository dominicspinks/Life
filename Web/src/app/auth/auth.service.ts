import { Injectable, signal } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private readonly JWT_TOKEN = 'JWT_TOKEN';
    private readonly REFRESH_TOKEN = 'REFRESH_TOKEN';
    private readonly apiUrl = environment.apiUrl;

    // Using signals for auth state
    private isLoggedInSignal = signal<boolean>(this.hasToken());
    isLoggedIn = this.isLoggedInSignal.asReadonly();

    constructor(private http: HttpClient, private router: Router) { }

    register(email: string, password: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/auth/register/`, { email, password });
    }

    login(email: string, password: string): Observable<any> {
        return this.http.post(`${this.apiUrl}/auth/login/`, { email, password })
            .pipe(
                tap(tokens => {
                    this.storeTokens(tokens);
                    this.isLoggedInSignal.set(true);
                })
            );
    }

    logout(): Observable<any> {
        const headers = new HttpHeaders({
            'Authorization': `Bearer ${this.getJwtToken()}`
        });

        return this.http.post(`${this.apiUrl}/auth/logout/`, {
            'refresh': this.getRefreshToken()
        }, { headers })
            .pipe(
                tap(() => {
                    this.removeTokens();
                    this.isLoggedInSignal.set(false);
                    this.router.navigate(['/login']);
                })
            );
    }

    refreshToken(): Observable<any> {
        return this.http.post(`${this.apiUrl}/auth/login/refresh/`, {
            'refresh': this.getRefreshToken()
        }).pipe(
            tap((tokens: any) => {
                this.storeJwtToken(tokens.access);
            })
        );
    }

    getJwtToken(): string {
        return localStorage.getItem(this.JWT_TOKEN) || '';
    }

    private hasToken(): boolean {
        return !!this.getJwtToken();
    }

    private getRefreshToken(): string {
        return localStorage.getItem(this.REFRESH_TOKEN) || '';
    }

    private storeJwtToken(jwt: string): void {
        localStorage.setItem(this.JWT_TOKEN, jwt);
    }

    private storeTokens(tokens: any): void {
        localStorage.setItem(this.JWT_TOKEN, tokens.access);
        localStorage.setItem(this.REFRESH_TOKEN, tokens.refresh);
    }

    private removeTokens(): void {
        localStorage.removeItem(this.JWT_TOKEN);
        localStorage.removeItem(this.REFRESH_TOKEN);
    }
}