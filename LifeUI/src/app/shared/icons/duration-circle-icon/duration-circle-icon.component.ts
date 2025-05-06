import { Component, input } from '@angular/core';

@Component({
    selector: 'app-duration-circle-icon',
    standalone: true,
    imports: [],
    templateUrl: './duration-circle-icon.component.html',
    styleUrl: './duration-circle-icon.component.css'
})
export class DurationCircleIconComponent {
    progress = input<number>(0);
}
