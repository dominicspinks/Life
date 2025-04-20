import { Injectable, signal } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, of, tap } from 'rxjs';
import { environment } from '../../../environments/environment';
import { jwtDecode } from 'jwt-decode';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private readonly JWT_TOKEN = 'JWT_TOKEN';
    private readonly REFRESH_TOKEN = 'REFRESH_TOKEN';
    private readonly USER_EMAIL = 'USER_EMAIL';
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
                    this.storeUserEmail(email);
                    this.isLoggedInSignal.set(true);
                })
            );
    }

    logout(): Observable<any> {
        return this.http.post(`${this.apiUrl}/auth/logout/`, {
            'refresh': this.getRefreshToken()
        })
            .pipe(
                tap(() => {
                    this.removeTokens();
                    localStorage.removeItem(this.USER_EMAIL);
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

    // New method to get user email
    getUserEmail(): Observable<string> {
        // Try to get email from localStorage first
        const storedEmail = localStorage.getItem(this.USER_EMAIL);
        if (storedEmail) {
            return of(storedEmail);
        }

        // If not in localStorage, try to extract from JWT token
        try {
            const token = this.getJwtToken();
            if (token) {
                const decoded: any = jwtDecode(token);
                if (decoded.email) {
                    this.storeUserEmail(decoded.email);
                    return of(decoded.email);
                }
            }
        } catch (error) {
            console.error('Error decoding JWT token:', error);
        }

        return of('');
    }

    getJwtToken(): string {
        return localStorage.getItem(this.JWT_TOKEN) || '';
    }

    private hasToken(): boolean {
        const token = this.getJwtToken();
        if (!token) return false;

        try {
            const decoded: any = jwtDecode(token);
            const now = Math.floor(Date.now() / 1000);
            return decoded.exp && decoded.exp > now;
        } catch (err) {
            console.error('Invalid JWT token', err);
            return false;
        }
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

    private storeUserEmail(email: string): void {
        localStorage.setItem(this.USER_EMAIL, email);
    }

    private removeTokens(): void {
        localStorage.removeItem(this.JWT_TOKEN);
        localStorage.removeItem(this.REFRESH_TOKEN);
    }
}