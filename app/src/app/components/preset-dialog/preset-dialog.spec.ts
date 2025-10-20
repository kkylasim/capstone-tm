import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PresetDialog } from './preset-dialog';

describe('PresetDialog', () => {
  let component: PresetDialog;
  let fixture: ComponentFixture<PresetDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PresetDialog]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PresetDialog);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
