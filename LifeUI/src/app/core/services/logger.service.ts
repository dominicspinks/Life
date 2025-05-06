import { Injectable, isDevMode } from '@angular/core';

type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'NONE';

@Injectable({
    providedIn: 'root',
})
export class LoggerService {
    private level: LogLevel = isDevMode() ? 'DEBUG' : 'ERROR';

    private shouldLog(level: LogLevel): boolean {
        const levels: LogLevel[] = ['DEBUG', 'INFO', 'WARNING', 'ERROR'];
        const currentIndex = levels.indexOf(this.level);
        const messageIndex = levels.indexOf(level);
        return messageIndex >= currentIndex;
    }

    debug(message: string, ...params: any[]) {
        if (isDevMode() && this.shouldLog('DEBUG')) {
            console.debug(`[DEBUG]: ${message}`, ...params);
        }
    }

    info(message: string, ...params: any[]) {
        if (isDevMode() && this.shouldLog('INFO')) {
            console.info(`[INFO]: ${message}`, ...params);
        }
    }

    warn(message: string, ...params: any[]) {
        if (this.shouldLog('WARNING')) {
            console.warn(`[WARNING]: ${message}`, ...params);
        }
    }

    error(message: string, ...params: any[]) {
        if (this.shouldLog('ERROR')) {
            console.error(`[ERROR]: ${message}`, ...params);
        }
    }
}
