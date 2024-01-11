#ifndef BUILDER_H
#define BUILDER_H

#include <QDialog>

namespace Ui {
class builder;
}

class builder : public QDialog
{
    Q_OBJECT

public:
    explicit builder(QWidget *parent = nullptr);
    ~builder();

private:
    Ui::builder *ui;
};

#endif // BUILDER_H
