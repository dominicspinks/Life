import { inject, Injectable } from '@angular/core';
import {
    HttpRequest,
    HttpHandler,
    HttpEvent,
    HttpInterceptor,
    HttpErrorResponse
} from '@angular/common/http';
import { AuthService } from './auth.service';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, filter, take, switchMap } from 'rxjs/operators';
import { excludedRoutes } from './excludedRoutes';

@Injectable()
export class TokenInterceptor implements HttpInterceptor {
    private authService = inject(AuthService);
    private isRefreshing = false;
    private refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(null);

    intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
        const isExcluded = excludedRoutes.some(route => request.url.includes(route));

        if (!isExcluded && this.authService.getJwtToken()) {
            request = this.addToken(request, this.authService.getJwtToken());
        }

        return next.handle(request).pipe(
            catchError(error => {
                const isExcluded = excludedRoutes.some(route => request.url.includes(route));

                if (!isExcluded && error instanceof HttpErrorResponse && error.status === 401) {
                    return this.handle401Error(request, next);
                } else {
                    return throwError(() => error);
                }
            })
        );
    }

    private addToken(request: HttpRequest<unknown>, token: string): HttpRequest<unknown> {
        return request.clone({
            setHeaders: {
                'Authorization': `Bearer ${token}`
            }
        });
    }

    private handle401Error(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
        if (!this.isRefreshing) {
            this.isRefreshing = true;
            this.refreshTokenSubject.next(null);

            return this.authService.refreshToken().pipe(
                switchMap((token: any) => {
                    this.isRefreshing = false;
                    this.refreshTokenSubject.next(token.access);
                    return next.handle(this.addToken(request, token.access));
                }),
                catchError((error) => {
                    this.isRefreshing = false;
                    this.authService.logout().subscribe();
                    return throwError(() => error);
                })
            );
        } else {
            return this.refreshTokenSubject.pipe(
                filter(token => token != null),
                take(1),
                switchMap(jwt => {
                    return next.handle(this.addToken(request, jwt));
                })
            );
        }
    }
}