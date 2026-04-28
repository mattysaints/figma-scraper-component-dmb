package com.digitalmodularbanking.dmbui

import android.content.Context
import android.os.Bundle
import android.os.Parcel
import android.text.InputType
import android.util.TypedValue
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.text.isDigitsOnly
import androidx.recyclerview.widget.RecyclerView
import com.digitalmodularbanking.app.R
import com.digitalmodularbanking.dmbui.widget.example.MyBottomSlidingPanelContentFragment
import com.digitalmodularbanking.dmbui.widget.example.MyRiepilogoFragment
import com.digitalmodularbanking.ui.alert.AlertManager
import com.digitalmodularbanking.ui.digitalexperience.UiConfiguration
import com.digitalmodularbanking.ui.dynamicfont.DynamicFontManager
import com.digitalmodularbanking.ui.dynamicfont.dimensions.FontName
import com.digitalmodularbanking.ui.dynamicfont.dimensions.FontWeight
import com.digitalmodularbanking.ui.dynamicfont.setTextWeight
import com.digitalmodularbanking.ui.extension.dpToPx
import com.digitalmodularbanking.ui.extension.getBitmapFromVectorDrawable
import com.digitalmodularbanking.ui.extension.setSafeOnClickListener
import com.digitalmodularbanking.ui.scopemanager.LayoutScope
import com.digitalmodularbanking.ui.utils.DIHelper
import com.digitalmodularbanking.ui.utils.model.DividerLengthConfiguration
import com.digitalmodularbanking.ui.widget.FormViewLinear
import com.digitalmodularbanking.ui.widget.UiComponentScrollView
import com.digitalmodularbanking.ui.widget.bottomslidingpanel.model.BottomSlidingPanelHeaderConfiguration
import com.digitalmodularbanking.ui.widget.calendar.model.BottomSlidingPanelCalendarHeaderConfiguration
import com.digitalmodularbanking.ui.widget.disclaimer.DisclaimerViewType
import com.digitalmodularbanking.ui.widget.dxcomponents.bottomslidingpanel.dialogfragment.DxBottomSlidingPanelDialogFragment
import com.digitalmodularbanking.ui.widget.dxcomponents.coretextlinkview.DxCoreTextLinkView
import com.digitalmodularbanking.ui.widget.dxcomponents.largetitletoolbar.DxLargeTitleToolbar
import com.digitalmodularbanking.ui.widget.dxcomponents.nextstep.nextstepfloatingbutton.DxNextStepFloatingButton
import com.digitalmodularbanking.ui.widget.dxcomponents.pulsantiera.DxPulsantiera
import com.digitalmodularbanking.ui.widget.dxcomponents.stepsprogressview.DxStepsProgressView
import com.digitalmodularbanking.ui.widget.dxcomponents.tooltipbutton.DxTooltipButton
import com.digitalmodularbanking.ui.widget.dxform.DxFormFieldFactory
import com.digitalmodularbanking.ui.widget.dxform.dxfields.dxtextlinkview.DxTextLinkViewField
import com.digitalmodularbanking.ui.widget.form.Field
import com.digitalmodularbanking.ui.widget.form.FormFieldListener
import com.digitalmodularbanking.ui.widget.form.FormManager
import com.digitalmodularbanking.ui.widget.form.Section
import com.digitalmodularbanking.ui.widget.form.ValidationRule
import com.digitalmodularbanking.ui.widget.form.fields.addressbookautocompleteview.AddressBookAutocompleteViewField
import com.digitalmodularbanking.ui.widget.form.fields.attachedimage.AttachedImageViewField
import com.digitalmodularbanking.ui.widget.form.fields.autocompletetextview.AutocompleteFormField
import com.digitalmodularbanking.ui.widget.form.fields.buttonview.ButtonViewField
import com.digitalmodularbanking.ui.widget.form.fields.calendardateview.CalendarDateViewField
import com.digitalmodularbanking.ui.widget.form.fields.checkbox.CheckBoxField
import com.digitalmodularbanking.ui.widget.form.fields.clickableitemview.ClickableItemViewField
import com.digitalmodularbanking.ui.widget.form.fields.contispinnerview.ContiSpinnerViewField
import com.digitalmodularbanking.ui.widget.form.fields.datetextview.DateTextViewField
import com.digitalmodularbanking.ui.widget.form.fields.dateview.DateViewField
import com.digitalmodularbanking.ui.widget.form.fields.disclaimerview.DisclaimerViewField
import com.digitalmodularbanking.ui.widget.form.fields.dividerview.DividerViewField
import com.digitalmodularbanking.ui.widget.form.fields.doublebuttonview.DoubleButtonViewField
import com.digitalmodularbanking.ui.widget.form.fields.f24scansionaview.CollapsibleImageViewField
import com.digitalmodularbanking.ui.widget.form.fields.gapview.GapViewField
import com.digitalmodularbanking.ui.widget.form.fields.imagetoggleview.ImageToggleViewField
import com.digitalmodularbanking.ui.widget.form.fields.imagewithlabelsview.ImageWithLabelsViewField
import com.digitalmodularbanking.ui.widget.form.fields.inputview.InputViewField
import com.digitalmodularbanking.ui.widget.form.fields.largedoublebuttonview.LargeDoubleButtonViewField
import com.digitalmodularbanking.ui.widget.form.fields.monthyearpickerview.MonthYearPickerViewField
import com.digitalmodularbanking.ui.widget.form.fields.multiplecheckbox.MultipleCheckBoxField
import com.digitalmodularbanking.ui.widget.form.fields.multiplerowsinputview.MultipleRowsInputViewField
import com.digitalmodularbanking.ui.widget.form.fields.passwordview.PasswordViewField
import com.digitalmodularbanking.ui.widget.form.fields.securityview.SecurityViewField
import com.digitalmodularbanking.ui.widget.form.fields.spinnerview.SpinnerViewField
import com.digitalmodularbanking.ui.widget.form.fields.titleform.TitleFormField
import com.digitalmodularbanking.ui.widget.form.fields.toggleview.ToggleViewField
import com.digitalmodularbanking.ui.widget.form.fields.tooltipview.TooltipViewField
import com.digitalmodularbanking.ui.widget.form.recyclerview.PlainListAdapter
import com.digitalmodularbanking.ui.widget.input.autocompleteinput.AddressbookAutocompleteDataParserInterface
import com.digitalmodularbanking.ui.widget.input.autocompleteinput.AutocompleteAdapter
import com.digitalmodularbanking.ui.widget.input.autocompleteinput.AutocompleteItem
import com.digitalmodularbanking.ui.widget.input.spinner.BaseSpinnerObject
import com.digitalmodularbanking.ui.widget.navigation.feedbackfandf.DIFeedbackHelper
import com.digitalmodularbanking.ui.widget.navigation.feedbackfandf.FeedbackFAndFDelegate
import com.digitalmodularbanking.ui.widget.navigation.utils.ActionButtonFactory
import com.digitalmodularbanking.ui.widget.pulsantiera.CTAType
import com.digitalmodularbanking.ui.widget.riepilogo.ClickListener
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoAdapterFactory
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoBitmapImageViewRow
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoButtonWithNextStep
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoButtonWithTextLink
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoCardView
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoCardViewWithCoreTextLink
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoCardViewWithTextLink
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoCheckDataTitleRow
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoCoreFloatingButtonInversedRow
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoCoreFloatingButtonRow
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoDigitalPaymentField
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoDivider
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoDoubleButton
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoDoubleButtonWithTextLink
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoDoubleText
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoField
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoFieldTable
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoGapViewRow
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoHeaderFieldWithImage
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoImageViewRow
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoPdfDownload
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoPulsantieraRow
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoTextFieldWithDotAndLink
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoTextLink
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoTextViewRow
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoTextViewWithDot
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoTextViewWithIconRow
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoTextWithInnerLink
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoTitleRow
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoTitleWithCTAElement
import com.digitalmodularbanking.ui.widget.riepilogo.DxRiepilogoUrlImageViewRow
import com.digitalmodularbanking.ui.widget.riepilogo.RiepilogoAdapterFactory
import com.digitalmodularbanking.ui.widget.riepilogo.RiepilogoStructureFactory
import com.digitalmodularbanking.ui.widget.textlink.CoreTextLinkListener
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.android.parcel.Parcelize
import java.util.Calendar
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity
    : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var buttonConfirm: Button
    private lateinit var nextStepButton: DxNextStepFloatingButton
    private lateinit var buttonGoToRiepilogo: Button
    var plainListAdapter = PlainListAdapter()

    private lateinit var header: BottomSlidingPanelHeaderConfiguration
    private lateinit var bottom: DxBottomSlidingPanelDialogFragment

    @Inject
    lateinit var alertManager: AlertManager

    @Inject
    lateinit var uiConfiguration: UiConfiguration

    @Inject
    lateinit var dynamicFontManager: DynamicFontManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        DIHelper.setUiConfiguration(uiConfiguration)
        DIHelper.scopeManager().activeScope = LayoutScope.Custom("new_ui")
        DIFeedbackHelper.init(object : FeedbackFAndFDelegate {
            override var isActive: Boolean = false
            override fun handleFeedbackBtn(context: Context) {}
        })
        setContentView(R.layout.activity_main)

        buttonConfirm = findViewById(R.id.bt_confirm)
        nextStepButton = findViewById(R.id.nextStepButton)
        buttonGoToRiepilogo = findViewById(R.id.goToRiepilogoButton)
        buttonGoToRiepilogo.setOnClickListener {
            supportFragmentManager.beginTransaction()
                .add(R.id.fragment_container, MyRiepilogoFragment(), "MyRiepilogoFragment")
                .addToBackStack(null)
                .commit()
        }


        nextStepButton.nextStepTextView.importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
        nextStepButton.button.text = "NextStepFloatingButton"
        nextStepButton.button.isEnabled = true
        nextStepButton.nextStepTextView.text = "NextStepFloatingButton nextStep"
        nextStepButton.button.setSafeOnClickListener {
            findViewById<DxStepsProgressView>(R.id.stepBar)?.moveProgress("flow0", 3, 3)
            findViewById<DxLargeTitleToolbar>(R.id.toolbar)?.collapseToolbar()
        }

        findViewById<ViewGroup>(R.id.scrollRoot).addView(ActionButtonFactory.makeCancelButton(context = this) { }, 0)

        findViewById<DxStepsProgressView>(R.id.stepBar)?.apply {
            setFlows(this@MainActivity, listOf("flow0"))
            moveProgress("flow0", 3, 3)
        }

        findViewById<DxLargeTitleToolbar>(R.id.toolbar)?.apply {
            setTitle("Dmb ui showcase")
        }
        findViewById<DxTooltipButton>(R.id.icon)?.apply{
            setButtonTooltipText(
               "il numero degli step è stato modificato, il numero degli step è stato modificato, il numero degli step è stato modificato, il numero degli step è stato modificato, il numero degli step è stato modificato, il numero degli step è stato modificato, il numero degli step è stato modificato,il numero degli step è stato modificato,il numero degli step è stato modificato, il numero degli step è stato modificato, il numero degli step è stato modificato, il numero degli step è stato modificato, il numero degli step è stato modificato, il numero degli step è stato modificato, il numero degli step è stato modificato, il numero degli step è stato modificato,il numero degli step è stato modificato,il numero degli step è stato modificato"
            )
            setOnClickListener {
                val positionTooltip = IntArray(2)
                getLocationOnScreen(positionTooltip)
                when {
                    rootView.height - positionTooltip[1] < height -> {
                        setTooltipGravity(Gravity.TOP)
                    }
                    else -> {
                        setTooltipGravity(Gravity.BOTTOM)
                    }
                }
                showTooltip()
            }
        }
        initForm()

        header = BottomSlidingPanelHeaderConfiguration(
            false,
            "TITOLO",
            "Sottotitolo",
            leftImage = resources.getIdentifier( R.drawable.dmb_ui_ic_disclaimer_green_success.toString(), "drawable",  this.packageName)
        )
        this.let { //
            bottom = DxBottomSlidingPanelDialogFragment(
                MyBottomSlidingPanelContentFragment(),
                false,
                header
            ).apply {
                isCancelable = false
            }
        }
    }

    private fun initForm() {
        val formManager = FormManager()
            .add(Field("11", TitleFormField("gqjpDxTitleFormElement")))
            .add(Field("1", TitleFormField("gqjpDxTitleFormElement")))
            .add(Field("AddressBookAutocompleteViewField2", AddressBookAutocompleteViewField(hint = "AddressBookAutocompleteViewFieldAddressBookAutocompleteViewField", scope = AddressbookAutocompleteDataParserInterface.SCOPE.BONIFICO, contacts = arrayListOf(), parser = ShowCaseAddressbookAutocompleteDataParserInterface(), tooltipField = TooltipViewField.Builder().addTitle("Title").addText("Text").build())))
            .add(Field("AddressBookAutocompleteViewField22", AddressBookAutocompleteViewField(hint = "AddressBookAutocompleteViewFieldAddressBookAutocompleteViewField", scope = AddressbookAutocompleteDataParserInterface.SCOPE.BONIFICO, contacts = arrayListOf(), parser = ShowCaseAddressbookAutocompleteDataParserInterface(), tooltipField = TooltipViewField.Builder().addTitle("Title").addText("Text").build())))
            .add(
                Field(
                    "ButtonViewField2",
                    ButtonViewField(
                        text = "${DxCoreTextLinkView.OPEN_TAG}Altre informazioni${DxCoreTextLinkView.CLOSING_TAG}",
                        icon = R.drawable.dmb_ui_ic_disclaimer_green_success,
                        textLinkColor = com.digitalmodularbanking.core.R.attr.coreLink,
                        marginTop = 16f,
                        action = {

                        }
                    )
                )
            )

            .add(Field("SecurityViewField", SecurityViewField()))
            .add(Section("section1", "Section"))
            .add(Section("section2", "Section2"))
            .add(GapViewField.newInstance())
            .add(Field("nome", InputViewField("InputViewElement", helperText = "Inserisci il nome"), listOf(OnlyLetterValidationRule())))
            .add(Field("password", PasswordViewField("PasswordViewElement", inputType = InputType.TYPE_CLASS_NUMBER)))
            .add(Field("data", DateViewField("DateViewElement"), listOf(OnlyFutureDateValidationRule())))
            .add(GapViewField.newInstance(50))
            .add(Field("data2", DateTextViewField("DxDateTextViewElement"), listOf(OnlyFutureDateValidationRule())))
            .add(GapViewField.newInstance("CustomGapViewField"))
            .add(
                Field(
                    "data3", CalendarDateViewField(
                        "DxCalendarDateViewElement", helperText = "gg.mm.aaaa", headerField = BottomSlidingPanelCalendarHeaderConfiguration(
                            true
                        ), fragmentManager = supportFragmentManager
                    ), listOf(OnlyFutureDateValidationRule())
                )
            )
            .add(GapViewField.newInstance("CustomGapViewField", 80))
            .add(
                Field(
                    "SpinnerViewField", SpinnerViewField(
                        "SpinnerViewElement", values = mutableListOf(
                            object : BaseSpinnerObject {
                                override fun toString(): String = "pippo"
                                override fun getHelperText(): String = "pippo"
                            },
                            object : BaseSpinnerObject {
                                override fun toString(): String = "pippo2"
                                override fun getHelperText(): String = "pippo2"
                            }
                        ))))
            .add(
                Field(
                    "ContiSpinnerViewField", ContiSpinnerViewField(
                        "ContiSpinnerViewElement",
                        object : BaseSpinnerObject {
                            override fun toString(): String = "pippo"
                            override fun getHelperText(): String = "pippo"
                        },
                        values = mutableListOf(
                            object : BaseSpinnerObject {
                                override fun toString(): String = "pippo"
                                override fun getHelperText(): String = "pippo"
                            },
                            object : BaseSpinnerObject {
                                override fun toString(): String = "pippo2"
                                override fun getHelperText(): String = "pippo2"
                            }
                        ))))
            .add(
                Field(
                    "ContiSpinnerViewField2", ContiSpinnerViewField(
                        "ContiSpinnerViewElement",
                        object : BaseSpinnerObject {
                            override fun toString(): String = "pippo"
                            override fun getHelperText(): String = "pippo"
                        },
                        values = mutableListOf(
                            object : BaseSpinnerObject {
                                override fun toString(): String = "pippo"
                                override fun getHelperText(): String = "pippo"
                            },
                        ))))
            .add(Field("CheckBoxField", CheckBoxField("CheckBoxElement"), validationRules = listOf(GenericValidationRule())))
            .add(Field("DxImageToggleViewElement", ImageToggleViewField(R.string.app_name, R.string.app_name, R.drawable.ic_launcher_foreground)))
            .add(Field("ToggleViewField", ToggleViewField("ToggleViewField")))
            .add(Field("DisclaimerViewField1", DisclaimerViewField(message = "DisclaimerViewField INFORMATIVE", disclaimerViewType = DisclaimerViewType.INFORMATIVE)))
            .add(Field("DisclaimerViewField2", DisclaimerViewField(message = "DisclaimerViewField ERROR", disclaimerViewType = DisclaimerViewType.ERROR)))
            .add(Field("DisclaimerViewField3", DisclaimerViewField(message = "DisclaimerViewField WARNING", disclaimerViewType = DisclaimerViewType.WARNING)))
            .add(Field("DisclaimerViewField4", DisclaimerViewField(message = "DisclaimerViewField SUCCESS", disclaimerViewType = DisclaimerViewType.SUCCESS)))
            .add(Field("DisclaimerViewField5", DisclaimerViewField(message = "DisclaimerViewField PROMO", disclaimerViewType = DisclaimerViewType.PROMO)))
            .add(Field("MonthYearPickerViewField", MonthYearPickerViewField(title = "MonthYearPickerViewField", tooltipField = TooltipViewField.Builder().addTitle("Title").addText("Text").build())))
            .add(Field("ImageWithLabelsViewField", ImageWithLabelsViewField(topText = "ImageWithLabelsViewField", bottomText = "ImageWithLabelsViewField")))
            .add(Field("ClickableItemViewField", ClickableItemViewField(title = "ClickableItemViewField", action = {})))
            .add(Field("ImageToggleViewField", ImageToggleViewField(R.string.app_name, R.string.conferma, com.digitalmodularbanking.ui.R.drawable.dmb_ui_green_square_with_rounded_borders, isEnabled = false)))
            .add(Field("DividerViewField1", DividerViewField()))
            .add(
                Field(
                    "MultipleCheckBoxField", MultipleCheckBoxField(
                        text1 = R.string.app_name,
                        text2 = R.string.app_name,
                        text3 = R.string.app_name,
                        text4 = R.string.app_name,
                        singleLine = false,
                        childMarginEnd = 0
                    )
                )
            )
            .add(Field("MultipleRowsInputViewField", MultipleRowsInputViewField(title = "MultipleRowsInputViewField", initValue = "Testo", lines = 3)))
            .add(Field("CollapsibleImageViewField", CollapsibleImageViewField(title = "CollapsibleImageViewField", getBitmapFromVectorDrawable(this, R.drawable.ic_launcher_foreground))))
            .add(Field("AddressBookAutocompleteViewField", AddressBookAutocompleteViewField(hint = "AddressBookAutocompleteViewFieldAddressBookAutocompleteViewField", scope = AddressbookAutocompleteDataParserInterface.SCOPE.BONIFICO, contacts = arrayListOf(), parser = ShowCaseAddressbookAutocompleteDataParserInterface(), tooltipField = TooltipViewField.Builder().addTitle("Title").addText("Text").build())))
            .add(Field("DxTextLinkViewField", DxTextLinkViewField(text = "DxTextLinkViewField ${DxCoreTextLinkView.OPEN_TAG}link${DxCoreTextLinkView.CLOSING_TAG}", paddingTop = 20)))
            .add(Field("AttachedImageViewField", AttachedImageViewField(attachedText = "AttachedImageViewField ${DxCoreTextLinkView.OPEN_TAG}link${DxCoreTextLinkView.CLOSING_TAG}", marginTop = 20f)))
            .add(Field("AutocompleteFormField", AutocompleteFormField(hint = "AutocompleteFormField", suggestions = arrayListOf("Acqua", "Albero", "Amore", "Amico", "Aperitivo", "Aprile", "Arancia", "Aereo", "Auto", "Avventura", "Anima", "Ala", "Ago", "Anello", "Arte", "Asino", "Aria", "Alto", "Azzurro", "Attore"))))
            .add(Field("LargeDoubleButtonViewField", LargeDoubleButtonViewField(firstButtonText = "LargeDoubleButtonViewField", secondButtonText = "secondButtonText", isFirstSelected = true)))
            .add(Field("DoubleButtonViewField", DoubleButtonViewField(firstButtonText = "DoubleButtonViewField", secondButtonText = "secondButtonText", firstDrawableRes = R.drawable.dmb_ui_double_button_selector, secondDrawableRes = R.drawable.dmb_ui_double_button_selector)))

        val formView: FormViewLinear = findViewById(R.id.form_view)
        formView.isNestedScrollingEnabled = false
        formView.init(
            formManager = formManager,
            formFieldListener = object : FormFieldListener {
                override fun manageExternalEvent(id: String, eventType: String?, data: Any?) {

                }

                override fun manageExternalError(id: String, validateErrorList: List<Error>) {
                    Toast.makeText(
                        this@MainActivity,
                        validateErrorList[0].message,
                        Toast.LENGTH_SHORT
                    ).show()
                }
            },
            formFieldFactory = DxFormFieldFactory()
        )

        val riepilogoView: UiComponentScrollView = findViewById(R.id.riepilogoView)
        riepilogoView.isNestedScrollingEnabled = false
        val riepilogoStructure = listOf(
            DxRiepilogoGapViewRow(),
            DxRiepilogoCheckDataTitleRow(true),
            DxRiepilogoGapViewRow(),
            DxRiepilogoTitleRow(title = "Titolo di prova", marginTop = 55),
            DxRiepilogoGapViewRow(),
            DxRiepilogoTitleWithCTAElement(title = "titolo di prova", ctaText = "cta text di prova", listener = DxRiepilogoTitleWithCTAElementListener()),
            DxRiepilogoGapViewRow(),
            DxRiepilogoPdfDownload(
                title = "Visaulizza i dati appena inseriti",
                buttonText = "Modulo F24",
                downloadPdf = object : ClickListener() {
                    override fun onClick(context: Context?) {
                        Toast.makeText(context, "Click sul download F24!", Toast.LENGTH_SHORT).show()
                    }

                    override fun describeContents(): Int {
                        TODO("Not yet implemented")
                    }

                    override fun writeToParcel(dest: Parcel, flags: Int) {
                        TODO("Not yet implemented")
                    }
                }
            ),
            DxRiepilogoGapViewRow(),
            DxRiepilogoHeaderFieldWithImage(title = "title prova", contentTitle = "content title prova", content = "content prova"),
            DxRiepilogoField(title = "title prova", contentTitle = "content title prova", content = "content prova", iconRes = com.digitalmodularbanking.ui.R.drawable.ic_star, paddingTop = 100, paddingBottom = 100),
            DxRiepilogoFieldTable(titleLeft = "titleLeft test", contentLeft = "contentLeft test", titleRight = "titleRight test", contentRight = "contentRight test", paddingTop = 15, paddingBottom = 15),
            DxRiepilogoTextLink(text = "testo di prova"),
            DxRiepilogoCardViewWithTextLink(text = "testo di {b}prova{/b}"),
            DxRiepilogoCoreFloatingButtonRow(mText = "testo di prova", clickListener = null),
            DxRiepilogoGapViewRow(),
            DxRiepilogoImageViewRow(image = R.drawable.dmb_ui_ic_disclaimer_blue_promo, height = 120.dpToPx(this), marginTop = 30, width = 110.dpToPx(this)),
            DxRiepilogoTextViewRow(text = "DxRiepilogoTextViewRow text example", textSize = 24.dpToPx(this), fontWeight = FontWeight.REGULAR, marginTop = 40, gravity = Gravity.CENTER, marginStart = 40, paddingBottom = 50),
            DxRiepilogoCardView(text = "Trovi l'operazione appena effettuata in", textLinkText = "Operazioni programmate", listener = null, disclaimerViewType = DisclaimerViewType.INFORMATIVE),
            DxRiepilogoDoubleButton(null, null, "prova 1", "prova 2"),
            DxRiepilogoButtonWithNextStep(buttonText = R.string.go_to_riepilogo, nextStepText = R.string.go_to_riepilogo, salvaEriprendiText = R.string.go_to_riepilogo, buttonListener = null, salvaEriprendiListener = null),
            DxRiepilogoTextWithInnerLink(text = "DxRiepilogoTextWithInnerLink --> Hai bisogno di aiuto? {b}PARLA CON NOI{/b}", mPaddingTop = 60, mPaddingBottom = 50, textLinkColor = com.digitalmodularbanking.core.R.attr.coreFill),
            DxRiepilogoButtonWithTextLink(buttonText = "DxRiepilogoButtonWithTextLink", text = "text"),
            DxRiepilogoPulsantieraRow(
                arrayListOf(
                    DxPulsantiera.CTA(
                        CTAType.REVOCA,
                        "nuova revoca",
                        null,
                        DxRiepilogoTitleWithCTAElementListener()
                    ),
                    DxPulsantiera.CTA(
                        CTAType.REVOCA,
                        "nuova revoca",
                        null,
                        null
                    ),
                    DxPulsantiera.CTA(
                        CTAType.REVOCA,
                        "nuova revoca",
                        null,
                        null
                    ),
                    DxPulsantiera.CTA(
                        CTAType.REVOCA,
                        "nuova revoca",
                        null,
                        null
                    ),
                    DxPulsantiera.CTA(
                        CTAType.REVOCA,
                        "nuova revoca",
                        null,
                        null
                    )
                )
            ),
            DxRiepilogoBitmapImageViewRow(),
            DxRiepilogoDivider(dividerLengthConfiguration = DividerLengthConfiguration.HORIZONTAL_PADDING),
            DxRiepilogoTextViewWithDot(text = "testo di prova", textColor = com.digitalmodularbanking.ui.R.color.black, textSize = 16, marginStart = 100, marginEnd = 100),
            DxRiepilogoTextFieldWithDotAndLink(text = "testo di prova", textColor = com.digitalmodularbanking.ui.R.color.black, textSize = 16, marginStart = 100, marginEnd = 100),
            DxRiepilogoDigitalPaymentField(title = "DxRiepilogoDigitalPaymentField", logoActivated = R.drawable.ic_launcher_foreground, logoDisabled = R.drawable.ic_launcher_foreground, actionImage = R.drawable.ic_launcher_foreground),
            DxRiepilogoUrlImageViewRow(image = "https://www.intesasanpaoloprivatebanking.it/bin/paginaGenerica/399/C_32_paginaGenerica_83_0_imgSinistra.png"),
            DxRiepilogoCoreFloatingButtonInversedRow(text = "DxRiepilogoCoreFloatingButtonInversedRow", null),
            DxRiepilogoDoubleButtonWithTextLink(
                upperButtonText = "DxRiepilogoDoubleButtonWithTextLink",
                bottomButtonText = "bottomButtonText",
                text = "text",
            ),
            DxRiepilogoCardViewWithCoreTextLink(
                coreTextLinkText = "DxRiepilogoCardViewWithCoreTextLink {b}prova{/b}",
                listener = object : CoreTextLinkListener() {
                    override fun onClick(context: Context?) {
                        Toast.makeText(context, "test", Toast.LENGTH_SHORT).show()
                    }

                    override fun describeContents(): Int {
                        TODO("Not yet implemented")
                    }

                    override fun writeToParcel(p0: Parcel, p1: Int) {
                        TODO("Not yet implemented")
                    }

                },
                marginStart = 40
            ),
            DxRiepilogoCardViewWithCoreTextLink(
                coreTextLinkText = "{b}Click per aprire bottomsheet{/b}",
                listener = object : CoreTextLinkListener() {
                    override fun onClick(context: Context?) {
                        bottom.show(supportFragmentManager, "MyBottomSlidingPanelContentFragment")
                    }

                    override fun describeContents(): Int {
                        TODO("Not yet implemented")
                    }

                    override fun writeToParcel(p0: Parcel, p1: Int) {
                        TODO("Not yet implemented")
                    }

                },
                marginStart = 40
            ),
            DxRiepilogoDoubleText(
                textLeft = "testo di prova sx",
                textLeftColor = com.digitalmodularbanking.core.R.attr.coreLabel,
                textLeftFontWeight = FontWeight.REGULAR,
                textRight = "testo di prova dx",
                textRightColor = com.digitalmodularbanking.core.R.attr.coreLabel,
                textRightFontWeight = FontWeight.MEDIUM,
                paddingTop = 10,
            ),
            DxRiepilogoTextViewWithIconRow(text = "testo di prova", marginStart = 60, marginTop = 20, fontWeight = FontWeight.REGULAR, icon = R.drawable.dmb_ui_ic_disclaimer_blue_info)
        )
        riepilogoView.apply {
            setProvider(DxRiepilogoAdapterFactory())
            setData(RiepilogoAdapterFactory().createAdapterList(RiepilogoStructureFactory.buildRiepilogoStructure(*riepilogoStructure.toTypedArray())))
        }

        buttonConfirm.setOnClickListener { formView.onConfirm() }
    }
}

@Parcelize
class DxRiepilogoTitleWithCTAElementListener : ClickListener() {
    override fun onClick(context: Context?) {
        context?.let {
            Toast.makeText(it, "prova", Toast.LENGTH_SHORT).show()
        }
    }
}

class ShowCaseAddressbookAutocompleteDataParserInterface : AddressbookAutocompleteDataParserInterface {
    override fun parseData(list: MutableList<AutocompleteItem>?, scope: AddressbookAutocompleteDataParserInterface.SCOPE): MutableList<Pair<Any, AutocompleteAdapter.AutoCompleteAssociatedValues>>? {
        return arrayListOf()
    }

    override fun getContactString(selectedContact: AutocompleteItem): String {
        return "getContactString"
    }

    override fun getOperation(selectedContact: AutocompleteItem, uniqueIdentifier: String, scope: AddressbookAutocompleteDataParserInterface.SCOPE): Any? {
        return Unit
    }
}

class GenericValidationRule : ValidationRule {
    override fun apply(any: Any?): Boolean {
        return false
    }

    override fun validationError(): String {
        return "Error"
    }

}

class OnlyFutureDateValidationRule : ValidationRule {
    override fun apply(any: Any?): Boolean {
        return (any as? Calendar)?.after(Calendar.getInstance()) ?: false
    }

    override fun validationError(): String {
        return "Date must be after today"
    }

}

class OnlyLetterValidationRule : ValidationRule {
    override fun apply(any: Any?): Boolean {
        return (any as? String)?.matches(Regex("^[a-zA-Z]+\$")) ?: false
    }

    override fun validationError(): String {
        return "Field can contain only letters"
    }

}

object AmountValidationRule : ValidationRule {
    override fun apply(any: Any?): Boolean {
        return (any as? String)?.isDigitsOnly() ?: false
    }

    override fun validationError(): String {
        return "Amount can contain only digits."
    }
}

class MyValidationRule : ValidationRule {
    override fun apply(any: Any?): Boolean {
        any?.let {
            val s = any as String
            return s.contains("A")
        }
        return false;
    }

    override fun validationError(): String {
        return "Il campo non contiene la lettera A"
    }

}

internal fun TextView.setTextViewDimens(
    dynamicFontManager: DynamicFontManager,
    maxWidth: Int? = null,
    maxHeight: Int? = null,
    textSize: FontName = FontName.FONT12,
    textWeight: FontWeight? = null,
    width: Int = -2,
    height: Int = -2,
    marginLeft: Int = 0,
    marginTop: Int = 0,
    marginRight: Int = 0,
    marginBottom: Int = 0,
) {
    setDimens(width, height, marginLeft, marginTop, marginRight, marginBottom)
    maxWidth?.let {
        this.maxWidth = it.dpToPx(context)
    }
    maxHeight?.let {
        this.maxHeight = it.dpToPx(context)
    }
    this.setTextSize(TypedValue.COMPLEX_UNIT_DIP, dynamicFontManager.getDimension(textSize).toFloat())
    textWeight?.let {
        this.setTextWeight(dynamicFontManager, it)
    }
}

internal fun View.setDimens(
    width: Int = -2,
    height: Int = -2,
    marginLeft: Int = 0,
    marginTop: Int = 0,
    marginRight: Int = 0,
    marginBottom: Int = 0,
) {
    layoutParams = (layoutParams as ViewGroup.MarginLayoutParams).also {
        it.width = if (width < 0) width else width.dpToPx(context)
        it.height = if (height < 0) height else height.dpToPx(context)
        it.setMargins(marginLeft.dpToPx(context), marginTop.dpToPx(context), marginRight.dpToPx(context), marginBottom.dpToPx(context))
    }
}