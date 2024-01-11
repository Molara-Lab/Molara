#include "builder.h"
#include "ui_builder.h"

builder::builder(QWidget *parent)
    : QDialog(parent)
    , ui(new Ui::builder)
{
    ui->setupUi(this);
}

builder::~builder()
{
    delete ui;
}
