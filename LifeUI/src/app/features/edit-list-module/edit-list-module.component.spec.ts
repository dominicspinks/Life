import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditListModuleComponent } from './edit-list-module.component';

describe('EditListModuleComponent', () => {
  let component: EditListModuleComponent;
  let fixture: ComponentFixture<EditListModuleComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditListModuleComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditListModuleComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
