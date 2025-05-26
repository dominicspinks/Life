import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';
import { registerLocaleData } from '@angular/common';
import localeEnAu from '@angular/common/locales/en-AU';

registerLocaleData(localeEnAu);

bootstrapApplication(AppComponent, appConfig)
    .catch(err => console.error(err));