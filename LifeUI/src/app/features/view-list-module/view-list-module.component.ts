import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
    selector: 'app-view-list-module',
    imports: [],
    templateUrl: './view-list-module.component.html'
})
export class ViewListModuleComponent {
    moduleId: number;

    constructor(private route: ActivatedRoute) {
        this.moduleId = Number(this.route.snapshot.paramMap.get('id'));
    }
}
