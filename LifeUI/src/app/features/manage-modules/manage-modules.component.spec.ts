import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManageModulesComponent } from './manage-modules.component';

describe('ManageModulesComponent', () => {
  let component: ManageModulesComponent;
  let fixture: ComponentFixture<ManageModulesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ManageModulesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ManageModulesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
