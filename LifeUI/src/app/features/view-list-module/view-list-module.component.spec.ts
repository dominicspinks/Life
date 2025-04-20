import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewListModuleComponent } from './view-list-module.component';

describe('ViewListModuleComponent', () => {
  let component: ViewListModuleComponent;
  let fixture: ComponentFixture<ViewListModuleComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ViewListModuleComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ViewListModuleComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
